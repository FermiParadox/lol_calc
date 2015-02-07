import sympy
import re

SYMPY_IMPORTED_AS = 'sympy' + '.'

#########################################################
# Your input
initial_str = 'a+myf1(myf2(a, b),y)'
function_names = { 'myf1(x,y)': 'cos(x*y)', 'myf2(a, b)': 'tan(a**b)'}
#########################################################

given_str = initial_str

# --------------------------------------------------
# SYMBOL DETECTION (x, y, z, mz,..)

# Prohibited symbols.
prohibited_symbol_names = set()
for method_name in dir(sympy):
    # (filters out private methods since they are irrelevant anyway)
    if method_name[0] != '_':
        prohibited_symbol_names.update(method_name)

# Converts "4x" to "4*x" etc.
pattern_digit_x = r"(\d)([A-Za-z])"
pattern_par_digit = r"(\))(\d)"
pattern_digit_par = r"[^a-zA-Z](\d)(\()"
for patt in (pattern_digit_x, pattern_par_digit, pattern_digit_par):
    given_str = re.sub(patt, r'\1*\2', given_str)

# Allowed examples: Na, x1, Xaasd, xa123
symbol_pattern = re.compile(r'[A-Za-z]+\d*')
symbols_in_given_str = re.findall(symbol_pattern, given_str)
# Filters out prohibited (and duplicate).
symbols_in_given_str = {i for i in symbols_in_given_str if (i not in prohibited_symbol_names)}

# Filters out functions
symbols_in_given_str = {i for i in symbols_in_given_str if i not in function_names}

# ----------------------------------------------------------------
# EXEC SYMBOL STRING
# e.g. " x, y, sd = sympy.symbols('x y sd') "
symbol_string_to_exec = ', '.join(symbols_in_given_str)
symbol_string_to_exec += ' = '
symbol_string_to_exec += "sympy.symbols('%s')" % ' '.join(symbols_in_given_str)

exec(symbol_string_to_exec)


# ----------------------------------------------------------------
# INSERT ALL CUSTOM FUNCTIONS

def fixed_power_op(str_to_fix):
    return str_to_fix.replace('^', '**')


# e.g. f1=sin(x) will be defined as def f1(x): return sin(x)
def function_as_executable_str(func_name, func_body):
    """
    Creates a string to be evaluated as an existing function.
    Function given must exist in sympy.

    :param func_name: (str) Includes the function arguments, e.g. "f1(x,y)"
    :param func_body: (str)
    :return: (str)
    """

    # Converts function names in function body to appropriate format
    # e.g. (x + ln(y)) -> (x + sympy.ln(y))
    for sympy_func_name in prohibited_symbol_names:
        sympy_func_full_name = SYMPY_IMPORTED_AS+sympy_func_name
        func_body = re.sub(r'%s' % sympy_func_name, sympy_func_full_name, func_body)

    # e.g. x^2, is x**2 in python
    func_body = fixed_power_op(func_body)

    string = '\ndef %s:' % func_name
    string += '\n    return %s' % func_body

    return string


def abstract_function_as_exec_str(func_name, func_body):

    string = '\n%s = %sFunction(%s)' % (func_name, SYMPY_IMPORTED_AS, func_body)

    return string


func_string_to_execute = [abstract_function_as_exec_str(i, function_names[i]) for i in function_names]
func_string_to_execute = '\n'.join(func_string_to_execute)

eval(func_string_to_execute)


# -------------------------------------------------------------------
# OUTPUT

# e.g. x^2, is x**2 in python
result = fixed_power_op(given_str)
for method_name in dir(sympy):
    # (filters out private methods since they are irrelevant anyway)
    result = result.replace(method_name, SYMPY_IMPORTED_AS+method_name)

final_result = eval(result)

print ('\n' + '-'*40)
print ('Functions: ')
for i in function_names:
    print (i, function_names[i])
print ('\nInitial string: ' + initial_str)
print ('Final string: ' + str(final_result) )
print ('\n' + '-'*10)