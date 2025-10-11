def transform(data, seed, arch_bits):
    result = bytearray(data if isinstance(data, bytes) else data.encode())
    for func in [_serpent_variant, _rc4_modified, _blowfish_lite, _twofish_basic, _idea_simple]:
        result = func(result, seed)
    return bytes(result)

def _serpent_variant(data, seed):
    sboxes = [_gen_sbox(seed + i * 11111) for i in range(8)]
    result = bytearray()
    for i, b in enumerate(data):
        sbox_idx = i % len(sboxes)
        result.append(sboxes[sbox_idx][b])
    return result

def _gen_sbox(seed):
    sbox = list(range(256))
    state = seed
    for i in range(255, 0, -1):
        state = (state * 2654435761) & 0xFFFFFFFF
        j = state % (i + 1)
        sbox[i], sbox[j] = sbox[j], sbox[i]
    return sbox

def _rc4_modified(data, seed):
    S = list(range(256))
    j = 0
    key = [(seed >> (i % 32)) & 0xFF for i in range(256)]
    for i in range(256):
        j = (j + S[i] + key[i]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    result = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        result.append(byte ^ K)
    return result

def _blowfish_lite(data, seed):
    P = [(seed * (i + 1)) & 0xFFFFFFFF for i in range(18)]
    result = bytearray()
    for i in range(0, len(data), 8):
        block = data[i:i+8]
        if len(block) < 8:
            block += bytes(8 - len(block))
        left = int.from_bytes(block[:4], 'big')
        right = int.from_bytes(block[4:8], 'big')
        for p in P:
            left ^= p
            right ^= _f_function(left, seed)
            left, right = right, left
        result.extend(left.to_bytes(4, 'big'))
        result.extend(right.to_bytes(4, 'big'))
    return result[:len(data)]

def _f_function(x, seed):
    return ((x * seed) ^ (x >> 16)) & 0xFFFFFFFF

def _twofish_basic(data, seed):
    key_dep_sbox = _gen_sbox(seed)
    result = bytearray()
    for i, b in enumerate(data):
        transformed = key_dep_sbox[b]
        transformed = ((transformed << 1) | (transformed >> 7)) & 0xFF
        transformed ^= ((seed >> (i % 24)) & 0xFF)
        result.append(transformed)
    return result

def _idea_simple(data, seed):
    key_parts = [(seed >> (i * 8)) & 0xFFFF for i in range(8)]
    result = bytearray()
    for i in range(0, len(data), 8):
        block = list(data[i:i+8])
        if len(block) < 8:
            block += [0] * (8 - len(block))
        for k in key_parts:
            for j in range(len(block)):
                block[j] = (block[j] * (k | 1)) & 0xFFFF
                block[j] = (block[j] + k) & 0xFFFF
                block[j] ^= k
        result.extend(b & 0xFF for b in block)
    return result[:len(data)]
