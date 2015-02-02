import sympy
import re

SYMPY_IMPORTED_AS = 'sympy' + '.'

#########################################################
# Your input
given_str = "-(a+b)+f1(f2(+x,y),z)-h"
function_names = {
    "f1(x,y)":"x+y**2",
    "f2(x,y)":"sin(x+y)"}
#########################################################

# --------------------------------------------------
# SYMBOL DETECTION (x, y, z, mz,..)

# Prohibited symbols.
prohibited_symbols = []
for method_name in dir(sympy):
    # (filters out private methods since they are irrelevant anyway)
    if method_name[0] != '_':
        prohibited_symbols.append(method_name)


symbol_pattern = re.compile(r'[A-Za-z]+')
symbols_in_given_str = re.findall(symbol_pattern, given_str)
# Filters out prohibited.
symbols_in_given_str = [i for i in symbols_in_given_str if (i not in prohibited_symbols)]

# Converts  "3x" to "x".
strings_to_remove = []
strings_to_insert = []
for symbol in symbols_in_given_str:
    if re.sub(r'\d+', '', symbol) != symbol:
        strings_to_remove.append(symbol)
        strings_to_insert.append(re.sub(r'\d+', '', symbol))

# Filters out duplicate.
symbols_in_given_str = frozenset(symbols_in_given_str)
# Filters out functions
symbols_in_given_str = [i for i in symbols_in_given_str if i not in function_names]

# ----------------------------------------------------------------
# EXEC SYMBOL STRING
# e.g. " x, y, sd = sympy.symbols('x y sd') "
symbol_string_to_exec = ', '.join(symbols_in_given_str)
symbol_string_to_exec += ' = '
symbol_string_to_exec += "sympy.symbols('%s')" % ' '.join(symbols_in_given_str)

exec(symbol_string_to_exec)


# ----------------------------------------------------------------
# INSERT ALL CUSTOM FUNCTIONS
# e.g. f1=sin(x) will be defined as def f1(x): return sin(x)
def function_as_executable_str(func_name, func_body):
    """
    Creates a string to be evaluated.

    :param func_name: (str) Includes the function arguments, e.g. "f1(x,y)"
    :param func_body: (str)
    :sympy_imported_as: (str)
    :return: str
    """

    # Converts function names in function body to appropriate format
    # e.g. (x + ln(y)) -> (x + sympy.ln(y))
    for sympy_func_name in prohibited_symbols:
        sympy_func_full_name = SYMPY_IMPORTED_AS+sympy_func_name
        func_body = re.sub(r'%s' % sympy_func_name, sympy_func_full_name, func_body)

    # e.g. x^2, is x**2 in python
    func_body = func_body.replace('^', '**')

    string = '\ndef %s:' % (func_name, )
    string += '\n    return %s' % func_body

    return string

func_string_to_execute = [function_as_executable_str(i, function_names[i]) for i in function_names]
func_string_to_execute = '\n'.join(func_string_to_execute)

exec(func_string_to_execute)


# OUTPUT
# -------------------------------------------------------------------
result = given_str.replace('^', '**')
for method_name in dir(sympy):
    # (filters out private methods since they are irrelevant anyway)
    result = result.replace(method_name, SYMPY_IMPORTED_AS+method_name)

exec('final_result = %s' % result)
print (final_result )