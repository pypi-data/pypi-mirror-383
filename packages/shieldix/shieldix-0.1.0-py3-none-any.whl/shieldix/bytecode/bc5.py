import marshal
import types
import sys

def compile_code(source, seed):
    code_obj = compile(source, '<secure>', 'exec')
    
    names = []
    for name in code_obj.co_names:
        encrypted_name = ''
        for i, ch in enumerate(name):
            encrypted_name += chr((ord(ch) + seed + i) % 256)
        names.append(encrypted_name)
    
    varnames = []
    for vname in code_obj.co_varnames:
        encrypted_vname = ''
        for i, ch in enumerate(vname):
            encrypted_vname += chr((ord(ch) - seed + i) % 256)
        varnames.append(encrypted_vname)
    
    if sys.version_info >= (3, 8):
        new_code = types.CodeType(
            code_obj.co_argcount, code_obj.co_posonlyargcount, code_obj.co_kwonlyargcount,
            code_obj.co_nlocals, code_obj.co_stacksize, code_obj.co_flags,
            code_obj.co_code, code_obj.co_consts, tuple(names), tuple(varnames),
            code_obj.co_filename, code_obj.co_name, code_obj.co_firstlineno,
            code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    else:
        new_code = types.CodeType(
            code_obj.co_argcount, code_obj.co_nlocals, code_obj.co_stacksize,
            code_obj.co_flags, code_obj.co_code, code_obj.co_consts, tuple(names),
            tuple(varnames), code_obj.co_filename, code_obj.co_name,
            code_obj.co_firstlineno, code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    
    return marshal.dumps(new_code)

def decompile_code(bytecode, seed):
    code_obj = marshal.loads(bytecode)
    
    names = []
    for name in code_obj.co_names:
        decrypted_name = ''
        for i, ch in enumerate(name):
            decrypted_name += chr((ord(ch) - seed - i) % 256)
        names.append(decrypted_name)
    
    varnames = []
    for vname in code_obj.co_varnames:
        decrypted_vname = ''
        for i, ch in enumerate(vname):
            decrypted_vname += chr((ord(ch) + seed - i) % 256)
        varnames.append(decrypted_vname)
    
    if sys.version_info >= (3, 8):
        restored = types.CodeType(
            code_obj.co_argcount, code_obj.co_posonlyargcount, code_obj.co_kwonlyargcount,
            code_obj.co_nlocals, code_obj.co_stacksize, code_obj.co_flags,
            code_obj.co_code, code_obj.co_consts, tuple(names), tuple(varnames),
            code_obj.co_filename, code_obj.co_name, code_obj.co_firstlineno,
            code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    else:
        restored = types.CodeType(
            code_obj.co_argcount, code_obj.co_nlocals, code_obj.co_stacksize,
            code_obj.co_flags, code_obj.co_code, code_obj.co_consts, tuple(names),
            tuple(varnames), code_obj.co_filename, code_obj.co_name,
            code_obj.co_firstlineno, code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    
    return restored
