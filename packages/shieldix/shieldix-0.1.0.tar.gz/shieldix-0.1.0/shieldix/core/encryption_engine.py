import sys
import os
import struct
import hashlib
import random
from shieldix.core import (
    layer1_transform, lyr2, lyr3, lyr4, lyr5, lyr6, lyr7, lyr8, lyr9, lyr10,
    lyr11, lyr12, lyr13, lyr14, lyr15, lyr16, lyr17, lyr18, lyr19, lyr20,
    lyr21, lyr22, lyr23, lyr24, lyr25, lyr26, lyr27, lyr28, lyr29, lyr30,
    phx31, xor32, enc33, crp34, sec35, sec36, sec37, sec38, sec39, sec40
)

class EncryptionEngine:
    def __init__(self, protection_level=3):
        self.protection_level = protection_level
        self.layers = [
            layer1_transform, lyr2, lyr3, lyr4, lyr5, lyr6, lyr7, lyr8, lyr9, lyr10,
            lyr11, lyr12, lyr13, lyr14, lyr15, lyr16, lyr17, lyr18, lyr19, lyr20,
            lyr21, lyr22, lyr23, lyr24, lyr25, lyr26, lyr27, lyr28, lyr29, lyr30,
            phx31, xor32, enc33, crp34, sec35, sec36, sec37, sec38, sec39, sec40
        ]
        self.arch_bits = self._detect_architecture()
        
    def _detect_architecture(self):
        bits = struct.calcsize("P") * 8
        return bits
        
    def _generate_seed(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        h = hashlib.sha256(data)
        for _ in range(100):
            h.update(h.digest())
        return struct.unpack('<Q', h.digest()[:8])[0]
        
    def encrypt(self, source_code):
        if isinstance(source_code, str):
            source_code = source_code.encode('utf-8')
            
        seed = self._generate_seed(source_code)
        random.seed(seed)
        
        encrypted = source_code
        layer_count = min(self.protection_level * 10, 40)
        
        for i in range(layer_count):
            layer_module = self.layers[i]
            encrypted = layer_module.transform(encrypted, seed, self.arch_bits)
            seed = self._generate_seed(encrypted)
            
        header = self._create_header(layer_count, seed)
        return header + encrypted
        
    def _create_header(self, layer_count, final_seed):
        magic = b'SLDX'
        version = struct.pack('<H', 1)
        layers = struct.pack('<B', layer_count)
        arch = struct.pack('<B', self.arch_bits)
        seed_bytes = struct.pack('<Q', final_seed)
        checksum = hashlib.sha256(magic + version + layers + arch + seed_bytes).digest()[:4]
        return magic + version + layers + arch + seed_bytes + checksum
    
    def decrypt(self, encrypted_data):
        header_size = 20
        if len(encrypted_data) < header_size:
            raise ValueError("Invalid encrypted data")
        
        header = encrypted_data[:header_size]
        encrypted_payload = encrypted_data[header_size:]
        
        magic = header[:4]
        if magic != b'SLDX':
            raise ValueError("Invalid file format")
        
        layer_count = struct.unpack('<B', header[6:7])[0]
        original_arch = struct.unpack('<B', header[7:8])[0]
        final_seed = struct.unpack('<Q', header[8:16])[0]
        
        decrypted = encrypted_payload
        seed = final_seed
        
        for i in range(layer_count - 1, -1, -1):
            layer_module = self.layers[i]
            decrypted = layer_module.reverse(decrypted, seed, self.arch_bits)
            if i > 0:
                seed = self._reverse_seed(decrypted)
        
        if isinstance(decrypted, bytes):
            decrypted = decrypted.decode('utf-8')
        
        return decrypted
    
    def _reverse_seed(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        h = hashlib.sha256(data)
        for _ in range(100):
            h.update(h.digest())
        return struct.unpack('<Q', h.digest()[:8])[0]
