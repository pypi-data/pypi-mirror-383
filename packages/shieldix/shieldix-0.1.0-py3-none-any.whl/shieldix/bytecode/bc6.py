import marshal
import types
import sys

def compile_code(source, seed):
    code_obj = compile(source, '<lock>', 'exec')
    
    consts = []
    for const in code_obj.co_consts:
        if isinstance(const, (int, float)):
            consts.append((const * seed) % 0xFFFFFFFF)
        elif isinstance(const, str):
            consts.append(''.join(chr((ord(c) ^ (seed & 0xFF)) % 256) for c in const))
        else:
            consts.append(const)
    
    bytecode = bytearray(code_obj.co_code)
    for i in range(len(bytecode)):
        bytecode[i] = (bytecode[i] + (seed >> (i % 32))) & 0xFF
    
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
    
    consts = []
    for const in code_obj.co_consts:
        if isinstance(const, (int, float)):
            consts.append((const // seed) if seed != 0 else const)
        elif isinstance(const, str):
            consts.append(''.join(chr((ord(c) ^ (seed & 0xFF)) % 256) for c in const))
        else:
            consts.append(const)
    
    protected_bytecode = bytearray(code_obj.co_code)
    for i in range(len(protected_bytecode)):
        protected_bytecode[i] = (protected_bytecode[i] - (seed >> (i % 32))) & 0xFF
    
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
