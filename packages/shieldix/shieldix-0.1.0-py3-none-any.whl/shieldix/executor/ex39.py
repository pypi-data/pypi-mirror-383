import struct
import sys

def exe(encrypted_data, seed=None, arch_bits=None):
    if arch_bits is None:
        arch_bits = struct.calcsize("P") * 8
    
    if seed is None:
        seed = _extract_seed_from_header(encrypted_data)
    
    decrypted = _decrypt_execution_layer(encrypted_data, seed, arch_bits, 39)
    
    code_obj = _reconstruct_code_object(decrypted, seed)
    
    exec_globals = {
        '__name__': '__main__',
        '__file__': '<protected>',
        '__builtins__': __builtins__,
    }
    
    exec(code_obj, exec_globals)
    
    return exec_globals

def _extract_seed_from_header(data):
    if len(data) < 20:
        return 0
    
    magic = data[:4]
    if magic[:2] == b'SL' or magic[:2] == b'BC' or magic[:2] == b'EX':
        return struct.unpack('<Q', data[8:16])[0]
    
    return 0

def _decrypt_execution_layer(data, seed, arch_bits, layer_id):
    state = seed + layer_id * 5555
    result = bytearray()
    
    for idx, byte in enumerate(data):
        state = (state * 80769 + 391) & 0xFFFFFFFF
        
        key = (state >> (idx % 20)) & 0xFF
        decrypted = byte ^ key
        
        decrypted = ((decrypted >> (layer_id % 8)) | (decrypted << (8 - layer_id % 8))) & 0xFF
        
        if arch_bits == 64:
            state = (state * 6364136223846793005) & 0xFFFFFFFFFFFFFFFF
            decrypted ^= (state >> 48) & 0xFF
        
        decrypted = (decrypted - ((state >> 8) & 0xFF)) & 0xFF
        
        result.append(decrypted)
    
    return bytes(result)

def _reconstruct_code_object(bytecode_data, seed):
    try:
        import marshal
        code_obj = marshal.loads(bytecode_data)
        return code_obj
    except:
        pass
    
    try:
        compiled = compile(bytecode_data.decode('utf-8'), '<protected>', 'exec')
        return compiled
    except:
        pass
    
    raise RuntimeError("Failed to reconstruct code object from protected data")

def execute_protected_module(file_path):
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    return exe(encrypted_data)
