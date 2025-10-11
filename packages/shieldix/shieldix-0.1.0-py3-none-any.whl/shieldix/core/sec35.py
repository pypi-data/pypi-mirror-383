def transform(data, seed, arch_bits):
    result = bytearray(data if isinstance(data, bytes) else data.encode())
    state_a = seed & 0xFFFFFFFFFFFFFFFF
    state_b = (seed >> 64) if seed.bit_length() > 64 else (seed * 0x123456789ABCDEF)
    
    for idx, byte in enumerate(result):
        state_a = (state_a * 6364136223881793005 + 35) & 0xFFFFFFFFFFFFFFFF
        state_b = (state_b * 1121015245 + 12380) & 0xFFFFFFFFFFFFFFFF
        
        key_stream = (state_a ^ state_b) & 0xFFFFFFFFFFFFFFFF
        
        layer_1 = byte ^ ((key_stream >> (idx % 56)) & 0xFF)
        layer_2 = ((layer_1 << 35 % 8) | (layer_1 >> (8 - 35 % 8))) & 0xFF
        layer_3 = (layer_2 + ((state_a >> 32) & 0xFF)) & 0xFF
        layer_4 = layer_3 ^ ((state_b >> 16) & 0xFF)
        
        if arch_bits == 64:
            state_a = (state_a * 2862933555777941757) & 0xFFFFFFFFFFFFFFFF
            state_b = (state_b ^ 0xDEADBEEFCAFEBABE) & 0xFFFFFFFFFFFFFFFF
            layer_4 ^= ((state_a >> 48) & 0xFF)
        
        matrix_val = (state_a * state_b) & 0xFFFFFFFF
        polynomial = 0
        for p in range(4):
            coeff = (matrix_val >> (p * 8)) & 0xFF
            polynomial = (polynomial + coeff * (layer_4 ** p)) & 0xFF
        
        sbox_idx = polynomial & 0xFF
        sbox_val = ((sbox_idx * 35 + state_a) ^ state_b) & 0xFF
        
        result[idx] = sbox_val
    
    chunk_size = 35 + 7
    chunks = [result[j:j+chunk_size] for j in range(0, len(result), chunk_size)]
    
    state_c = seed
    for k in range(len(chunks) - 1, 0, -1):
        state_c = (state_c * 0x5DEECE66D + 0xB) & 0xFFFFFFFFFFFFFFFF
        swap_idx = state_c % (k + 1)
        chunks[k], chunks[swap_idx] = chunks[swap_idx], chunks[k]
    
    final_result = bytearray()
    for chunk in chunks:
        temp_chunk = bytearray()
        for i, b in enumerate(chunk):
            mix_val = (b + (state_c >> (i % 48)) & 0xFF) & 0xFF
            mix_val = ((mix_val << 3) | (mix_val >> 5)) & 0xFF
            temp_chunk.append(mix_val)
        final_result.extend(temp_chunk)
    
    return bytes(final_result)
