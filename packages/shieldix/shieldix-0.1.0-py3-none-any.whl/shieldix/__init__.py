__version__ = "0.1.0"
__author__ = "MERO"
__telegram__ = "@QP4RM"

import struct
import hashlib

def protect(source_code, output_file=None, protection_level=3):
    if isinstance(source_code, str):
        source_code_bytes = source_code.encode('utf-8')
    else:
        source_code_bytes = source_code
    
    h = hashlib.sha256(source_code_bytes)
    for _ in range(100):
        h.update(h.digest())
    base_seed = struct.unpack('<Q', h.digest()[:8])[0]
    
    layer_count = min(protection_level * 10, 40)
    
    encrypted = bytearray(source_code_bytes)
    
    for layer in range(layer_count):
        seed = base_seed + layer * 1000
        for i in range(len(encrypted)):
            key_state = (seed * (i + 1) + layer * 7919) & 0xFFFFFFFFFFFFFFFF
            key = (key_state >> (i % 56)) & 0xFF
            encrypted[i] ^= key
    
    magic = b'SLDX'
    version = struct.pack('<H', 1)
    layers = struct.pack('<B', layer_count)
    arch = struct.pack('<B', struct.calcsize("P") * 8)
    seed_bytes = struct.pack('<Q', base_seed)
    checksum = hashlib.sha256(magic + version + layers + arch + seed_bytes + bytes(encrypted)).digest()[:4]
    
    header = magic + version + layers + arch + seed_bytes + checksum
    encrypted_data = header + bytes(encrypted)
    
    if output_file:
        with open(output_file, 'wb') as f:
            f.write(encrypted_data)
        return output_file
    
    return encrypted_data

def execute_protected(encrypted_file):
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()
    
    header_size = 20
    if len(encrypted_data) < header_size:
        raise ValueError("Invalid encrypted data")
    
    header = encrypted_data[:header_size]
    encrypted_payload = encrypted_data[header_size:]
    
    magic = header[:4]
    if magic != b'SLDX':
        raise ValueError("Invalid file format")
    
    layer_count = struct.unpack('<B', header[6:7])[0]
    base_seed = struct.unpack('<Q', header[8:16])[0]
    
    decrypted = bytearray(encrypted_payload)
    
    for layer in range(layer_count - 1, -1, -1):
        seed = base_seed + layer * 1000
        for i in range(len(decrypted)):
            key_state = (seed * (i + 1) + layer * 7919) & 0xFFFFFFFFFFFFFFFF
            key = (key_state >> (i % 56)) & 0xFF
            decrypted[i] ^= key
    
    source_code = bytes(decrypted).decode('utf-8')
    
    exec_globals = {
        '__name__': '__main__',
        '__file__': encrypted_file,
        '__builtins__': __builtins__,
    }
    
    exec(source_code, exec_globals)
    return exec_globals

__all__ = [
    'protect',
    'execute_protected'
]
