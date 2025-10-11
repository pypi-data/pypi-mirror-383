import marshal
import types
import sys

def compile_code(source, seed):
    code_obj = compile(source, '<shielded>', 'exec')
    
    bytecode = bytearray(code_obj.co_code)
    key_stream = []
    state = seed
    for i in range(len(bytecode)):
        state = (state * 0x41C64E6D + 0x3039) & 0xFFFFFFFF
        key_stream.append(state & 0xFF)
    
    for i in range(len(bytecode)):
        bytecode[i] ^= key_stream[i]
    
    new_code = types.CodeType(
        code_obj.co_argcount,
        code_obj.co_kwonlyargcount if sys.version_info >= (3, 0) else 0,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        bytes(bytecode),
        code_obj.co_consts,
        code_obj.co_names,
        code_obj.co_varnames,
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
        bytes(bytecode),
        code_obj.co_consts,
        code_obj.co_names,
        code_obj.co_varnames,
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
    
    protected_bytecode = bytearray(code_obj.co_code)
    key_stream = []
    state = seed
    for i in range(len(protected_bytecode)):
        state = (state * 0x41C64E6D + 0x3039) & 0xFFFFFFFF
        key_stream.append(state & 0xFF)
    
    for i in range(len(protected_bytecode)):
        protected_bytecode[i] ^= key_stream[i]
    
    restored = types.CodeType(
        code_obj.co_argcount,
        code_obj.co_kwonlyargcount if sys.version_info >= (3, 0) else 0,
        code_obj.co_nlocals,
        code_obj.co_stacksize,
        code_obj.co_flags,
        bytes(protected_bytecode),
        code_obj.co_consts,
        code_obj.co_names,
        code_obj.co_varnames,
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
        bytes(protected_bytecode),
        code_obj.co_consts,
        code_obj.co_names,
        code_obj.co_varnames,
        code_obj.co_filename,
        code_obj.co_name,
        code_obj.co_firstlineno,
        code_obj.co_lnotab,
        code_obj.co_freevars,
        code_obj.co_cellvars
    )
    
    return restored
