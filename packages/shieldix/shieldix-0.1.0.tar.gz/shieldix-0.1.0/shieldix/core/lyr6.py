def transform(data, seed, arch_bits):
    result = bytearray(data if isinstance(data, bytes) else data.encode())
    for func in [_vigenere_poly, _block_cipher_custom, _stream_xor_multi, _transposition_complex, _rail_fence_dynamic]:
        result = func(result, seed, arch_bits)
    return bytes(result)

def _vigenere_poly(data, seed, arch_bits):
    key_len = 16 if arch_bits == 64 else 8
    key = [(seed >> (i*8)) & 0xFF for i in range(key_len)]
    return bytearray((b + key[i % len(key)]) & 0xFF for i, b in enumerate(data))

def _block_cipher_custom(data, seed, arch_bits):
    block_size = 16
    result = bytearray()
    for i in range(0, len(data), block_size):
        block = data[i:i+block_size]
        state = seed + i
        encrypted_block = bytearray()
        for b in block:
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            encrypted_block.append(b ^ (state & 0xFF))
        result.extend(encrypted_block)
    return result

def _stream_xor_multi(data, seed, arch_bits):
    generators = [lambda s: (s * 1103515245 + 12345) & 0x7FFFFFFF,
                  lambda s: (s * 69069 + 1) & 0xFFFFFFFF,
                  lambda s: (s ^ (s >> 11)) & 0xFFFFFFFF]
    result = bytearray()
    states = [seed + i * 7919 for i in range(len(generators))]
    for b in data:
        combined = 0
        for i, gen in enumerate(generators):
            states[i] = gen(states[i])
            combined ^= (states[i] & 0xFF)
        result.append(b ^ combined)
    return result

def _transposition_complex(data, seed, arch_bits):
    cols = 8 if arch_bits == 64 else 6
    rows = (len(data) + cols - 1) // cols
    matrix = [[0] * cols for _ in range(rows)]
    idx = 0
    for i in range(rows):
        for j in range(cols):
            if idx < len(data):
                matrix[i][j] = data[idx]
                idx += 1
    col_order = list(range(cols))
    state = seed
    for i in range(len(col_order) - 1, 0, -1):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        j = state % (i + 1)
        col_order[i], col_order[j] = col_order[j], col_order[i]
    result = bytearray()
    for col in col_order:
        for row in range(rows):
            if len(result) < len(data):
                result.append(matrix[row][col])
    return result

def _rail_fence_dynamic(data, seed, arch_bits):
    rails = (seed % 5) + 3
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    for b in data:
        fence[rail].append(b)
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction = -direction
    result = bytearray()
    for rail_data in fence:
        result.extend(rail_data)
    return result
