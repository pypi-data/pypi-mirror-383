import struct
import hashlib
import os

def generate_secure_seed():
    random_bytes = os.urandom(32)
    h = hashlib.sha512(random_bytes)
    return struct.unpack('<Q', h.digest()[:8])[0]

def compute_hash(data, algorithm='sha256'):
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if algorithm == 'sha256':
        h = hashlib.sha256(data)
    elif algorithm == 'sha512':
        h = hashlib.sha512(data)
    elif algorithm == 'md5':
        h = hashlib.md5(data)
    else:
        h = hashlib.sha256(data)
    
    return h.hexdigest()

def xor_bytes(data1, data2):
    result = bytearray()
    max_len = max(len(data1), len(data2))
    
    for i in range(max_len):
        byte1 = data1[i % len(data1)] if data1 else 0
        byte2 = data2[i % len(data2)] if data2 else 0
        result.append(byte1 ^ byte2)
    
    return bytes(result)

def rotate_left(value, shift, bits=8):
    shift = shift % bits
    mask = (1 << bits) - 1
    return ((value << shift) | (value >> (bits - shift))) & mask

def rotate_right(value, shift, bits=8):
    shift = shift % bits
    mask = (1 << bits) - 1
    return ((value >> shift) | (value << (bits - shift))) & mask

def bytes_to_hex(data):
    return ''.join(format(b, '02x') for b in data)

def hex_to_bytes(hex_string):
    return bytes.fromhex(hex_string)

def detect_architecture():
    bits = struct.calcsize("P") * 8
    return bits

def pad_data(data, block_size=16):
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    padding_length = block_size - (len(data) % block_size)
    padding = bytes([padding_length] * padding_length)
    
    return data + padding

def unpad_data(data):
    if not data:
        return data
    
    padding_length = data[-1]
    
    if padding_length > len(data) or padding_length == 0:
        return data
    
    for i in range(1, padding_length + 1):
        if data[-i] != padding_length:
            return data
    
    return data[:-padding_length]
