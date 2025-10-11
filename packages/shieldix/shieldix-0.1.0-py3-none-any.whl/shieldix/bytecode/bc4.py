import marshal
import types
import sys

def compile_code(source, seed):
    code_obj = compile(source, '<shield>', 'exec')
    
    bytecode = bytearray(code_obj.co_code)
    permutation = list(range(len(bytecode)))
    state = seed
    for i in range(len(permutation) - 1, 0, -1):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        j = state % (i + 1)
        permutation[i], permutation[j] = permutation[j], permutation[i]
    
    shuffled = bytearray(len(bytecode))
    for i, idx in enumerate(permutation):
        shuffled[idx] = bytecode[i]
    
    header = seed.to_bytes(8, 'little') + len(bytecode).to_bytes(4, 'little')
    
    if sys.version_info >= (3, 8):
        new_code = types.CodeType(
            code_obj.co_argcount, code_obj.co_posonlyargcount, code_obj.co_kwonlyargcount,
            code_obj.co_nlocals, code_obj.co_stacksize, code_obj.co_flags,
            bytes(shuffled), code_obj.co_consts, code_obj.co_names, code_obj.co_varnames,
            code_obj.co_filename, code_obj.co_name, code_obj.co_firstlineno,
            code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    else:
        new_code = types.CodeType(
            code_obj.co_argcount, code_obj.co_nlocals, code_obj.co_stacksize,
            code_obj.co_flags, bytes(shuffled), code_obj.co_consts, code_obj.co_names,
            code_obj.co_varnames, code_obj.co_filename, code_obj.co_name,
            code_obj.co_firstlineno, code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    
    return header + marshal.dumps(new_code)

def decompile_code(bytecode, seed):
    header = bytecode[:12]
    original_seed = int.from_bytes(header[:8], 'little')
    original_len = int.from_bytes(header[8:12], 'little')
    
    code_obj = marshal.loads(bytecode[12:])
    
    shuffled = bytearray(code_obj.co_code)
    permutation = list(range(len(shuffled)))
    state = original_seed
    for i in range(len(permutation) - 1, 0, -1):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        j = state % (i + 1)
        permutation[i], permutation[j] = permutation[j], permutation[i]
    
    restored_bytecode = bytearray(len(shuffled))
    for i, idx in enumerate(permutation):
        restored_bytecode[i] = shuffled[idx]
    
    if sys.version_info >= (3, 8):
        restored = types.CodeType(
            code_obj.co_argcount, code_obj.co_posonlyargcount, code_obj.co_kwonlyargcount,
            code_obj.co_nlocals, code_obj.co_stacksize, code_obj.co_flags,
            bytes(restored_bytecode), code_obj.co_consts, code_obj.co_names, code_obj.co_varnames,
            code_obj.co_filename, code_obj.co_name, code_obj.co_firstlineno,
            code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    else:
        restored = types.CodeType(
            code_obj.co_argcount, code_obj.co_nlocals, code_obj.co_stacksize,
            code_obj.co_flags, bytes(restored_bytecode), code_obj.co_consts, code_obj.co_names,
            code_obj.co_varnames, code_obj.co_filename, code_obj.co_name,
            code_obj.co_firstlineno, code_obj.co_lnotab, code_obj.co_freevars, code_obj.co_cellvars
        )
    
    return restored
