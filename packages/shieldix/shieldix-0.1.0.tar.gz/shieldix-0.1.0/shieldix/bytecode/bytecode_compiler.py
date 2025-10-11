import struct
import marshal
from shieldix.bytecode import (bc1, bc2, bc3, bc4, bc5, bc6, bc7, bc8, bc9, bc10,
                                bc11, bc12, bc13, bc14, bc15, bc16, bc17, bc18, bc19, bc20,
                                bc21, bc22, bc23, bc24, bc25, bc26, bc27, bc28, bc29, bc30)

class BytecodeCompiler:
    def __init__(self, protection_level=3):
        self.protection_level = protection_level
        self.compilers = [bc1, bc2, bc3, bc4, bc5, bc6, bc7, bc8, bc9, bc10,
                         bc11, bc12, bc13, bc14, bc15, bc16, bc17, bc18, bc19, bc20,
                         bc21, bc22, bc23, bc24, bc25, bc26, bc27, bc28, bc29, bc30]
        self.arch_bits = struct.calcsize("P") * 8
    
    def compile(self, source_code, seed):
        bytecode = source_code
        
        compiler_count = min(self.protection_level * 5, 30)
        
        for i in range(compiler_count):
            compiler_module = self.compilers[i]
            bytecode = compiler_module.compile_code(bytecode, seed + i * 1111)
        
        return bytecode
    
    def decompile(self, bytecode, seed):
        result = bytecode
        
        compiler_count = min(self.protection_level * 5, 30)
        
        for i in range(compiler_count - 1, -1, -1):
            compiler_module = self.compilers[i]
            result = compiler_module.decompile_code(result, seed + i * 1111)
        
        return result
