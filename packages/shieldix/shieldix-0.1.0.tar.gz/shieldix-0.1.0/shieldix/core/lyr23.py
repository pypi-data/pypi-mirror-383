def transform(data, seed, arch_bits):
    result = bytearray(data if isinstance(data, bytes) else data.encode())
    state = seed + 23 * 999
    
    for idx, byte in enumerate(result):
        state = (state * 1103538245 + 14645) & 0x7FFFFFFF
        key_byte = (state >> (idx % 24)) & 0xFF
        
        transformed = byte ^ key_byte
        transformed = ((transformed << 23 % 8) | (transformed >> (8 - 23 % 8))) & 0xFF
        transformed = (transformed + ((state >> 8) & 0xFF)) & 0xFF
        transformed ^= ((seed >> (idx % 16)) & 0xFF)
        
        if arch_bits == 64:
            state = (state * 6364136223846793005) & 0xFFFFFFFFFFFFFFFF
            transformed ^= (state >> 32) & 0xFF
        
        result[idx] = transformed
    
    chunk_size = 23 + 5
    chunks = [result[j:j+chunk_size] for j in range(0, len(result), chunk_size)]
    state = seed
    
    for k in range(len(chunks) - 1, 0, -1):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        swap_idx = state % (k + 1)
        chunks[k], chunks[swap_idx] = chunks[swap_idx], chunks[k]
    
    final_result = bytearray()
    for chunk in chunks:
        final_result.extend(chunk)
    
    return bytes(final_result)
