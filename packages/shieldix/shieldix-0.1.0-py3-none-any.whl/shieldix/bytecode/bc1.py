import marshal
import types
import sys

def compile_code(source, seed):
    code_obj = compile(source, '<protected>', 'exec')
    
    consts = list(code_obj.co_consts)
    for i in range(len(consts)):
        if isinstance(consts[i], (int, float)):
            consts[i] = consts[i] ^ (seed & 0xFFFFFFFF)
    
    names = tuple(n[::-1] for n in code_obj.co_names)
    
    varnames = tuple(v[::-1] for v in code_obj.co_varnames)
    
    new_code = types.CodeType(
        code_obj.co_argcount,
        code_obj.co_kwonlyargcount if sys.version_info >= (3, 0) else 0,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        tuple(consts),
        names,
        varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        code_obj.co_lnotab,
        code_obj.co_freevars,
        code_obj.co_cellvars
    ) if sys.version_info >= (3, 8) else types.CodeType(
        code_obj.co_argcount,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        tuple(consts),
        names,
        varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        code_obj.co_lnotab,
        code_obj.co_freevars,
        code_obj.co_cellvars
    )
    
    return marshal.dumps(new_code)

def decompile_code(bytecode, seed):
    code_obj = marshal.loads(bytecode)
    
    consts = list(code_obj.co_consts)
    for i in range(len(consts)):
        if isinstance(consts[i], (int, float)):
            consts[i] = consts[i] ^ (seed & 0xFFFFFFFF)
    
    names = tuple(n[::-1] for n in code_obj.co_names)
    
    varnames = tuple(v[::-1] for v in code_obj.co_varnames)
    
    restored = types.CodeType(
        code_obj.co_argcount,
        code_obj.co_kwonlyargcount if sys.version_info >= (3, 0) else 0,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        tuple(consts),
        names,
        varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        code_obj.co_lnotab,
        code_obj.co_freevars,
        code_obj.co_cellvars
    ) if sys.version_info >= (3, 8) else types.CodeType(
        code_obj.co_argcount,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        code_obj.co_code,
        tuple(consts),
        names,
        varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        code_obj.co_lnotab,
        code_obj.co_freevars,
        code_obj.co_cellvars
    )
    
    return restored
