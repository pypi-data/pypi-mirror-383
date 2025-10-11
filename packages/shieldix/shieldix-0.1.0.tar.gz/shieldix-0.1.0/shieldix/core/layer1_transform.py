import struct
import hashlib

def transform(data, seed, arch_bits):
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    result = bytearray()
    key_stream = _generate_keystream(seed, len(data), arch_bits)
    
    for i, byte in enumerate(data):
        transformed = (byte ^ key_stream[i]) & 0xFF
        transformed = _rotate_left(transformed, (i % 8))
        transformed = _substitute_byte(transformed, i, seed)
        result.append(transformed)
    
    result = _permute_blocks(result, seed)
    result = _add_noise(result, seed, arch_bits)
    result = _matrix_transform(result, seed)
    result = _fibonacci_mix(result, seed)
    result = _prime_scramble(result, seed)
    result = _cascade_xor(result, seed)
    result = _bit_interleave(result, seed)
    result = _polynomial_transform(result, seed)
    result = _dynamic_shuffle(result, seed)
    
    return bytes(result)

def _generate_keystream(seed, length, arch_bits):
    keystream = bytearray()
    state = seed
    
    for i in range(length):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        if arch_bits == 64:
            state = (state * 6364136223846793005 + 1442695040888963407) & 0xFFFFFFFFFFFFFFFF
        
        h = hashlib.sha256(struct.pack('<Q', state))
        keystream.append(h.digest()[i % 32])
    
    return keystream

def _rotate_left(byte, count):
    count = count % 8
    return ((byte << count) | (byte >> (8 - count))) & 0xFF

def _rotate_right(byte, count):
    count = count % 8
    return ((byte >> count) | (byte << (8 - count))) & 0xFF

def _substitute_byte(byte, position, seed):
    sbox = _generate_sbox(seed)
    return sbox[byte]

def _generate_sbox(seed):
    sbox = list(range(256))
    state = seed
    
    for i in range(255, 0, -1):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        j = state % (i + 1)
        sbox[i], sbox[j] = sbox[j], sbox[i]
    
    return sbox

def _permute_blocks(data, seed):
    block_size = 16
    blocks = [data[i:i+block_size] for i in range(0, len(data), block_size)]
    
    state = seed
    indices = list(range(len(blocks)))
    
    for i in range(len(indices) - 1, 0, -1):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        j = state % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    
    result = bytearray()
    for idx in indices:
        result.extend(blocks[idx])
    
    return result

def _add_noise(data, seed, arch_bits):
    noise_positions = _generate_noise_positions(len(data), seed, arch_bits)
    result = bytearray(data)
    
    for pos in noise_positions:
        if pos < len(result):
            noise_byte = _generate_noise_byte(pos, seed)
            result[pos] = (result[pos] + noise_byte) & 0xFF
    
    return result

def _generate_noise_positions(length, seed, arch_bits):
    positions = []
    state = seed
    count = max(length // 10, 1)
    
    for _ in range(count):
        state = (state * 48271) % 2147483647
        if arch_bits == 64:
            state = (state * 6364136223846793005) & 0xFFFFFFFFFFFFFFFF
        positions.append(state % length)
    
    return positions

def _generate_noise_byte(position, seed):
    h = hashlib.sha256(struct.pack('<Q', seed + position))
    return h.digest()[0]

def _matrix_transform(data, seed):
    size = len(data)
    matrix_size = int(size ** 0.5) + 1
    matrix = [[0] * matrix_size for _ in range(matrix_size)]
    
    idx = 0
    for i in range(matrix_size):
        for j in range(matrix_size):
            if idx < size:
                matrix[i][j] = data[idx]
                idx += 1
    
    state = seed
    for i in range(matrix_size):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        offset = state % matrix_size
        matrix[i] = matrix[i][offset:] + matrix[i][:offset]
    
    result = bytearray()
    for i in range(matrix_size):
        for j in range(matrix_size):
            if len(result) < size:
                result.append(matrix[i][j])
    
    return result

def _fibonacci_mix(data, seed):
    fib = _generate_fibonacci(len(data), seed)
    result = bytearray()
    
    for i, byte in enumerate(data):
        mixed = (byte + fib[i]) & 0xFF
        result.append(mixed)
    
    return result

def _generate_fibonacci(length, seed):
    fib = []
    a, b = seed % 256, (seed >> 8) % 256
    
    for _ in range(length):
        fib.append(a % 256)
        a, b = b, (a + b) % 256
    
    return fib

def _prime_scramble(data, seed):
    primes = _generate_primes(len(data))
    result = bytearray()
    
    for i, byte in enumerate(data):
        prime_idx = i % len(primes)
        scrambled = (byte * primes[prime_idx]) & 0xFF
        result.append(scrambled)
    
    return result

def _generate_primes(n):
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
              73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
              157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
              239, 241, 251]
    
    while len(primes) < n:
        primes.extend(primes)
    
    return primes[:n]

def _cascade_xor(data, seed):
    result = bytearray()
    cascade = seed & 0xFF
    
    for byte in data:
        xored = byte ^ cascade
        result.append(xored)
        cascade = (cascade + xored) & 0xFF
    
    return result

def _bit_interleave(data, seed):
    if len(data) < 2:
        return data
    
    result = bytearray()
    state = seed
    
    for i in range(0, len(data) - 1, 2):
        byte1 = data[i]
        byte2 = data[i + 1]
        
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        if state % 2 == 0:
            interleaved1 = ((byte1 & 0xAA) | (byte2 & 0x55))
            interleaved2 = ((byte1 & 0x55) | (byte2 & 0xAA))
        else:
            interleaved1 = ((byte1 & 0xF0) | (byte2 & 0x0F))
            interleaved2 = ((byte1 & 0x0F) | (byte2 & 0xF0))
        
        result.append(interleaved1)
        result.append(interleaved2)
    
    if len(data) % 2 == 1:
        result.append(data[-1])
    
    return result

def _polynomial_transform(data, seed):
    coefficients = _generate_polynomial_coefficients(seed)
    result = bytearray()
    
    for i, byte in enumerate(data):
        poly_value = 0
        for power, coeff in enumerate(coefficients):
            poly_value += coeff * (byte ** power)
        result.append(poly_value & 0xFF)
    
    return result

def _generate_polynomial_coefficients(seed):
    coefficients = []
    state = seed
    
    for i in range(8):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        coefficients.append(state % 256)
    
    return coefficients

def _dynamic_shuffle(data, seed):
    indices = list(range(len(data)))
    state = seed
    
    for i in range(len(indices) - 1, 0, -1):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        j = state % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    
    result = bytearray()
    for idx in indices:
        result.append(data[idx])
    
    return result
