import struct

def transform(data, seed, arch_bits):
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    result = bytearray(data)
    
    result = _spiral_encode(result, seed)
    result = _galois_field_mix(result, seed)
    result = _inverse_permutation(result, seed)
    result = _wave_transform(result, seed)
    result = _modular_arithmetic(result, seed, arch_bits)
    result = _bit_plane_decompose(result, seed)
    result = _cellular_automata(result, seed)
    result = _fractal_mixing(result, seed)
    result = _chaotic_map(result, seed)
    result = _histogram_equalization(result, seed)
    
    return bytes(result)

def _spiral_encode(data, seed):
    size = len(data)
    dim = int(size ** 0.5) + 1
    matrix = [[0] * dim for _ in range(dim)]
    
    idx = 0
    for i in range(dim):
        for j in range(dim):
            if idx < size:
                matrix[i][j] = data[idx]
                idx += 1
    
    result = bytearray()
    top, bottom, left, right = 0, dim - 1, 0, dim - 1
    direction = (seed >> 3) % 4
    
    while top <= bottom and left <= right:
        if direction == 0:
            for i in range(left, right + 1):
                if len(result) < size:
                    result.append(matrix[top][i])
            top += 1
        elif direction == 1:
            for i in range(top, bottom + 1):
                if len(result) < size:
                    result.append(matrix[i][right])
            right -= 1
        elif direction == 2:
            for i in range(right, left - 1, -1):
                if len(result) < size:
                    result.append(matrix[bottom][i])
            bottom -= 1
        else:
            for i in range(bottom, top - 1, -1):
                if len(result) < size:
                    result.append(matrix[i][left])
            left += 1
        
        direction = (direction + 1) % 4
    
    return result

def _galois_field_mix(data, seed):
    gf_table = _generate_gf256_table(seed)
    result = bytearray()
    
    for i, byte in enumerate(data):
        mixed = gf_table[byte] ^ ((seed >> (i % 8)) & 0xFF)
        result.append(mixed)
    
    return result

def _generate_gf256_table(seed):
    table = [0] * 256
    state = seed & 0xFF
    
    for i in range(256):
        table[i] = state
        state = _gf_multiply(state, 3) ^ ((seed >> ((i % 4) * 8)) & 0xFF)
    
    return table

def _gf_multiply(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit_set = a & 0x80
        a <<= 1
        if hi_bit_set:
            a ^= 0x1B
        b >>= 1
    return p & 0xFF

def _inverse_permutation(data, seed):
    indices = list(range(len(data)))
    state = seed
    
    for i in range(len(indices)):
        state = (state * 2654435761) & 0xFFFFFFFF
        j = state % len(indices)
        indices[i], indices[j] = indices[j], indices[i]
    
    inverse_indices = [0] * len(indices)
    for i, idx in enumerate(indices):
        inverse_indices[idx] = i
    
    result = bytearray()
    for idx in inverse_indices:
        result.append(data[idx])
    
    return result

def _wave_transform(data, seed):
    result = bytearray()
    amplitude = (seed & 0xFF) / 255.0
    frequency = ((seed >> 8) & 0xFF) / 50.0
    
    for i, byte in enumerate(data):
        wave_offset = int(amplitude * 127 * _sine_approx(frequency * i))
        transformed = (byte + wave_offset) & 0xFF
        result.append(transformed)
    
    return result

def _sine_approx(x):
    x = x % (2 * 3.14159265359)
    if x < 0:
        x += 2 * 3.14159265359
    
    if x < 3.14159265359:
        return 4 * x * (3.14159265359 - x) / (3.14159265359 * 3.14159265359)
    else:
        x -= 3.14159265359
        return -(4 * x * (3.14159265359 - x) / (3.14159265359 * 3.14159265359))

def _modular_arithmetic(data, seed, arch_bits):
    modulus = 257 if arch_bits == 64 else 251
    multiplier = (seed % (modulus - 1)) + 1
    result = bytearray()
    
    for byte in data:
        transformed = (byte * multiplier) % modulus
        result.append(transformed & 0xFF)
    
    return result

def _bit_plane_decompose(data, seed):
    planes = [bytearray() for _ in range(8)]
    
    for byte in data:
        for bit_pos in range(8):
            bit = (byte >> bit_pos) & 1
            planes[bit_pos].append(bit)
    
    state = seed
    shuffled_planes = []
    for plane in planes:
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        offset = state % len(plane)
        shuffled = plane[offset:] + plane[:offset]
        shuffled_planes.append(shuffled)
    
    result = bytearray()
    for i in range(len(data)):
        byte = 0
        for bit_pos in range(8):
            if i < len(shuffled_planes[bit_pos]):
                byte |= (shuffled_planes[bit_pos][i] << bit_pos)
        result.append(byte)
    
    return result

def _cellular_automata(data, seed):
    rule = (seed & 0xFF)
    generations = 3
    
    cells = list(data)
    
    for _ in range(generations):
        new_cells = [0] * len(cells)
        for i in range(len(cells)):
            left = cells[i - 1] if i > 0 else 0
            center = cells[i]
            right = cells[i + 1] if i < len(cells) - 1 else 0
            
            config = ((left & 1) << 2) | ((center & 1) << 1) | (right & 1)
            new_cells[i] = ((rule >> config) & 1) * 255
        
        cells = [(cells[i] + new_cells[i]) & 0xFF for i in range(len(cells))]
    
    return bytearray(cells)

def _fractal_mixing(data, seed):
    result = bytearray()
    
    for i, byte in enumerate(data):
        x = byte / 255.0
        iterations = (seed >> (i % 8)) % 10 + 1
        
        for _ in range(iterations):
            x = x * x + ((seed >> 16) & 0xFF) / 255.0
            x = x % 1.0
        
        result.append(int(x * 255) & 0xFF)
    
    return result

def _chaotic_map(data, seed):
    result = bytearray()
    r = 3.9 + ((seed & 0xFF) / 2550.0)
    x = ((seed >> 8) & 0xFF) / 255.0
    
    for byte in data:
        x = r * x * (1 - x)
        chaos_value = int(x * 255)
        result.append(byte ^ chaos_value)
    
    return result

def _histogram_equalization(data, seed):
    histogram = [0] * 256
    for byte in data:
        histogram[byte] += 1
    
    cdf = [0] * 256
    cdf[0] = histogram[0]
    for i in range(1, 256):
        cdf[i] = cdf[i - 1] + histogram[i]
    
    cdf_min = min(cdf)
    total = len(data)
    
    lookup = [0] * 256
    for i in range(256):
        if total - cdf_min > 0:
            lookup[i] = int(((cdf[i] - cdf_min) / (total - cdf_min)) * 255)
        else:
            lookup[i] = i
        lookup[i] = (lookup[i] ^ ((seed >> (i % 8)) & 0xFF)) & 0xFF
    
    result = bytearray()
    for byte in data:
        result.append(lookup[byte])
    
    return result
