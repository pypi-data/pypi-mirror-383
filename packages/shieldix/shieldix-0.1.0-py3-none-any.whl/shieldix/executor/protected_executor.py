import struct
from shieldix.executor import (ex1, ex2, ex3, ex4, ex5, ex6, ex7, ex8, ex9, ex10,
                                ex11, ex12, ex13, ex14, ex15, ex16, ex17, ex18, ex19, ex20,
                                ex21, ex22, ex23, ex24, ex25, ex26, ex27, ex28, ex29, ex30,
                                ex31, ex32, ex33, ex34, ex35, ex36, ex37, ex38, ex39, ex40,
                                ex41, ex42, ex43, ex44, ex45)

class ProtectedExecutor:
    def __init__(self):
        self.executors = [ex1, ex2, ex3, ex4, ex5, ex6, ex7, ex8, ex9, ex10,
                         ex11, ex12, ex13, ex14, ex15, ex16, ex17, ex18, ex19, ex20,
                         ex21, ex22, ex23, ex24, ex25, ex26, ex27, ex28, ex29, ex30,
                         ex31, ex32, ex33, ex34, ex35, ex36, ex37, ex38, ex39, ex40,
                         ex41, ex42, ex43, ex44, ex45]
        self.arch_bits = struct.calcsize("P") * 8
    
    def exe(self, encrypted_file_or_data):
        if isinstance(encrypted_file_or_data, str):
            with open(encrypted_file_or_data, 'rb') as f:
                encrypted_data = f.read()
        else:
            encrypted_data = encrypted_file_or_data
        
        seed = self._extract_seed(encrypted_data)
        
        decrypted = encrypted_data
        for i, executor_module in enumerate(self.executors):
            decrypted = executor_module.exe(decrypted, seed + i * 2222, self.arch_bits)
            if isinstance(decrypted, dict):
                return decrypted
        
        return None
    
    def _extract_seed(self, data):
        if len(data) < 20:
            return 0
        
        magic = data[:4]
        if magic in [b'SLDX', b'BC\x00\x00', b'EX\x00\x00']:
            try:
                return struct.unpack('<Q', data[8:16])[0]
            except:
                return 0
        
        return 0
