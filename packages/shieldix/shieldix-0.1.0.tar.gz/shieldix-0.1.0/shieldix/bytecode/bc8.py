import marshal
import types
import sys

def compile_code(source, seed):
    code_obj = compile(source, '<feistel_network>', 'exec')
    
    
    bytecode = bytearray(code_obj.co_code)
    transform_key = (seed * 0x8888) & 0xFFFFFFFFFFFFFFFF
    
    
    for i in range(len(bytecode)):
        transform_key = (transform_key * 0x8888) & 0xFFFFFFFFFFFFFFFF
        rotation = (transform_key >> (i % 56)) & 0x7
        byte_val = bytecode[i]
        bytecode[i] = ((byte_val << rotation) | (byte_val >> (8 - rotation))) & 0xFF
        bytecode[i] ^= (transform_key >> (i % 32)) & 0xFF
    
    
    consts = []
    for const in code_obj.co_consts:
        if isinstance(const, int):
            consts.append((const ^ seed) & 0xFFFFFFFF)
        elif isinstance(const, str):
            enc_str = ''.join(chr((ord(c) + (seed % 127)) % 256) for c in const)
            consts.append(enc_str)
        else:
            consts.append(const)
    
    if sys.version_info >= (3, 8):
        new_code = types.CodeType(
            code_obj.co_argcount, code_obj.co_posonlyargcount, code_obj.co_kwonlyargcount,
            code_obj.co_nlocals, code_obj.co_stacksize, code_obj.co_flags,
            bytes(bytecode), tuple(consts), code_obj.co_names, code_obj.co_varnames,
            code_obj.co_filename, code_obj.co_name, code_obj.co_firstlineno,
            code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    else:
        new_code = types.CodeType(
            code_obj.co_argcount, code_obj.co_nlocals, code_obj.co_stacksize,
            code_obj.co_flags, bytes(bytecode), tuple(consts), code_obj.co_names,
            code_obj.co_varnames, code_obj.co_filename, code_obj.co_name,
            code_obj.co_firstlineno, code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    
    return marshal.dumps(new_code)

def decompile_code(bytecode, seed):
    code_obj = marshal.loads(bytecode)
    
    
    protected_bytecode = bytearray(code_obj.co_code)
    transform_key = (seed * 0x8888) & 0xFFFFFFFFFFFFFFFF
    
    for i in range(len(protected_bytecode)):
        transform_key = (transform_key * 0x8888) & 0xFFFFFFFFFFFFFFFF
        rotation = (transform_key >> (i % 56)) & 0x7
        protected_bytecode[i] ^= (transform_key >> (i % 32)) & 0xFF
        byte_val = protected_bytecode[i]
        protected_bytecode[i] = ((byte_val >> rotation) | (byte_val << (8 - rotation))) & 0xFF
    
    
    consts = []
    for const in code_obj.co_consts:
        if isinstance(const, int):
            consts.append((const ^ seed) & 0xFFFFFFFF)
        elif isinstance(const, str):
            dec_str = ''.join(chr((ord(c) - (seed % 127)) % 256) for c in const)
            consts.append(dec_str)
        else:
            consts.append(const)
    
    if sys.version_info >= (3, 8):
        restored = types.CodeType(
            code_obj.co_argcount, code_obj.co_posonlyargcount, code_obj.co_kwonlyargcount,
            code_obj.co_nlocals, code_obj.co_stacksize, code_obj.co_flags,
            bytes(protected_bytecode), tuple(consts), code_obj.co_names, code_obj.co_varnames,
            code_obj.co_filename, code_obj.co_name, code_obj.co_firstlineno,
            code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    else:
        restored = types.CodeType(
            code_obj.co_argcount, code_obj.co_nlocals, code_obj.co_stacksize,
            code_obj.co_flags, bytes(protected_bytecode), tuple(consts), code_obj.co_names,
            code_obj.co_varnames, code_obj.co_filename, code_obj.co_name,
            code_obj.co_firstlineno, code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    
    return restored
