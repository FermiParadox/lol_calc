import sympy as sp    

P, V, n, R, T = sp.symbols('P V n R T')
IDEAL_GAS_EQUATION = P*V - n*R*T   


def f(x, values_dct, eq_lst):
    """
    Solves equations in eq_lst for x, substitutes values from values_dct, and returns value of x.

    :param x: Sympy symbol
    :param values_dct: Dict with sympy symbols as keys, and numbers as values.
    """

    lst = []
    lst += eq_lst

    for i, j in values_dct.items():
        lst.append(sp.Eq(i, j))

    try:
        return sp.solve(lst)[0][x]
    except IndexError:
        print('This equation has no solutions.')

vals = {P: 2, n: 3, R: 1, T:4}

r = f(V, values_dct=vals, eq_lst=[IDEAL_GAS_EQUATION, ])
print(r)   # Prints 6