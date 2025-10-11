import marshal
import types
import sys

def compile_code(source, seed):
    code_obj = compile(source, '<encrypted>', 'exec')
    
    consts = []
    for c in code_obj.co_consts:
        if isinstance(c, str):
            encrypted_str = ''.join(chr((ord(ch) + seed) % 256) for ch in c)
            consts.append(encrypted_str)
        else:
            consts.append(c)
    
    lnotab = bytearray(code_obj.co_lnotab)
    for i in range(len(lnotab)):
        lnotab[i] = (lnotab[i] + (seed >> (i % 8))) & 0xFF
    
    new_code = types.CodeType(
        code_obj.co_argcount,
        code_obj.co_kwonlyargcount if sys.version_info >= (3, 0) else 0,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        tuple(consts),
        code_obj.co_names,
        code_obj.co_varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        bytes(lnotab),
        code_obj.co_freevars,
        code_obj.co_cellvars
    ) if sys.version_info >= (3, 8) else types.CodeType(
        code_obj.co_argcount,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        tuple(consts),
        code_obj.co_names,
        code_obj.co_varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        bytes(lnotab),
        code_obj.co_freevars,
        code_obj.co_cellvars
    )
    
    return marshal.dumps(new_code)

def decompile_code(bytecode, seed):
    code_obj = marshal.loads(bytecode)
    
    consts = []
    for c in code_obj.co_consts:
        if isinstance(c, str):
            decrypted_str = ''.join(chr((ord(ch) - seed) % 256) for ch in c)
            consts.append(decrypted_str)
        else:
            consts.append(c)
    
    lnotab = bytearray(code_obj.co_lnotab)
    for i in range(len(lnotab)):
        lnotab[i] = (lnotab[i] - (seed >> (i % 8))) & 0xFF
    
    restored = types.CodeType(
        code_obj.co_argcount,
        code_obj.co_kwonlyargcount if sys.version_info >= (3, 0) else 0,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        tuple(consts),
        code_obj.co_names,
        code_obj.co_varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        bytes(lnotab),
        code_obj.co_freevars,
        code_obj.co_cellvars
    ) if sys.version_info >= (3, 8) else types.CodeType(
        code_obj.co_argcount,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        tuple(consts),
        code_obj.co_names,
        code_obj.co_varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        bytes(lnotab),
        code_obj.co_freevars,
        code_obj.co_cellvars
    )
    
    return restored
