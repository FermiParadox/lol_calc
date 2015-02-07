import re
import sympy


##################################################
# Input string and functions
given_str = 'a+myf1(myf2(a, b),y)+sin(cos(x+z))'
given_functions = {'myf1(x,y)': 'cross(x,y)',
                   'myf2(a, b)': 'value(a,b)'}
##################################################


processed_str = given_str


def fixed_power_op(str_to_fix):
    return str_to_fix.replace('^', '**')


def fixed_multiplication(str_to_fix):
    """
    Inserts multiplication symbol wherever omitted.
    """
    
    pattern_digit_x = r"(\d)([A-Za-z])"         # 4x -> 4*x
    pattern_par_digit = r"(\))(\d)"             # )4 -> )*4
    pattern_digit_par = r"[^a-zA-Z]?_?(\d)(\()"  # 4( -> 4*(
    
    for patt in (pattern_digit_x, pattern_par_digit, pattern_digit_par):
        str_to_fix = re.sub(patt, r'\1*\2', str_to_fix)
    
    return str_to_fix


processed_str = fixed_power_op(processed_str)


class FProcessing(object):

    def __init__(self, func_key, func_body):
        self.func_key = func_key
        self.func_body = func_body

    def sliced_func_name(self):
        return re.sub(r'(.+)\(.+', r'\1', self.func_key)

    def sliced_func_args(self):
        return re.search(r'\((.*)\)', self.func_key).group()

    def sliced_args(self):
        """
        Returns arguments found for given function. Arguments can be separated by comma or whitespace.

        :returns (list)
        """

        if ',' in self.sliced_func_args():
            arg_separator = ','
        else:
            arg_separator = ' '

        return self.sliced_func_args().replace('(', '').replace(')', '').split(arg_separator)

    def num_of_sliced_args(self):
        """
        Returns number of arguments found for given function.
        """
        return len(self.sliced_args())

    def functions_in_function_body(self):
        """
        Detects functions in function body.

        e.g. f1(x,y): sin(x+y**2), will result in "sin"

        :returns (set)
        """

        return set(re.findall(r'([a-zA-Z]+_\w*)\(', self.func_body))

    def symbols_in_func_body(self):
        """
        Detects non argument symbols in function body.
        """

        symbols_in_body = set(re.findall(r'[a-zA-Z]+_\w*', self.func_body))

        return symbols_in_body - self.functions_in_function_body()


# --------------------------------------------------------------------------------------
# SYMBOL DETECTION (x, y, z, mz,..)


# Prohibited symbols
prohibited_symbol_names = set()
# Custom function names are prohibited symbol names.
for key in given_functions.keys():
    prohibited_symbol_names |= {FProcessing(func_key=key, func_body=None).sliced_func_name()}


def symbols_in_str(provided_str):

    """
    Returns a set of symbol names that are contained in provided string.

    Allowed symbols start with a letter followed by 0 or more letters,
    and then 0 or more numbers (eg. x, x1, Na, Xaa_sd, xa123)
    """
    symbol_pattern = re.compile(r'[A-Za-z]+\d*')
    symbol_name_set = re.findall(symbol_pattern, provided_str)
    # Filters out prohibited.
    symbol_name_set = {i for i in symbol_name_set if (i not in prohibited_symbol_names)}

    return symbol_name_set


# ----------------------------------------------------------------
# EXEC SYMBOLS
symbols_in_given_str = symbols_in_str(given_str)
# e.g. " x, y, sd = sympy.symbols('x y sd') "
symbol_string_to_exec = ', '.join(symbols_in_given_str)
symbol_string_to_exec += ' = '
symbol_string_to_exec += "sympy.symbols('%s')" % ' '.join(symbols_in_given_str)

exec(symbol_string_to_exec)


# -----------------------------------------------------------------------------------------
# FUNCTIONS


def secondary_function_as_exec_str(func_key):
    """
    Used for functions that are contained in the function body of given_functions.

    E.g.  given_functions = {f1(x): sin(4+x)}

    "my_f1 = sympy.Function('sin')(x)"

    :param func_key: (str)
    :return: (str)
    """

    return "\n%s = sympy.Function('%s')(%s)" % (func_key, func_key, FProcessing(func_key=func_key,
                                                                                func_body=None).sliced_args())


def exec_given_function_as_sympy_class(func_key, func_body):
    """
    Converts given_function to sympy class and executes it. 

    E.g.    class f1(sympy.Function):
                nargs = (1, 2)

                @classmethod
                def eval(cls, x, y):
                    return cross(x+y**2)

    :param func_key: (str)
    :return: (None)
    """

    func_proc_instance = FProcessing(func_key=func_key, func_body=func_body)

    returned_str = 'class %s(sympy.Function): ' % func_proc_instance.sliced_func_name()
    returned_str += '\n\tnargs = %s' % func_proc_instance.num_of_sliced_args()
    returned_str += '\n\t@classmethod'

    returned_str += '\n\tdef eval(cls, %s):' % ','.join(func_proc_instance.sliced_args())
    returned_str = returned_str.replace("'", '')

    returned_str += '\n\t\treturn %s' % func_body

    print(returned_str)
    exec(returned_str)


symbols_in_function_bodies = set()

# Exec


# Executes given_functions
for key, val in given_functions.items():
    exec_given_function_as_sympy_class(func_key=key, func_body=val)

eval('sympy')

final_result = eval(given_str)



















