from scipy.integrate import quad
from scipy.special import jn
from scipy import exp, zeros, linspace
from scipy.linalg import norm
 
Inf = float("inf")
 
K = [5, 3, 2]
 
 
def f(lmbd, a, b):
    l = b - a
    return exp(-2 * b * lmbd) * (-1 - 2 * b * lmbd + 4 * K[2]) \
    + exp(-2 * (b + l) * lmbd) * (1 + 2 * a * lmbd - 4 * K[2]) \
    + exp(-2 * l * lmbd) * (2 + 4 * l * lmbd - 8 * K[2]) \
    + 2 * exp(2 * a * lmbd) * (2 * K[2] + a * lmbd) ** 2 \
    + 2 * exp(-4 * l * lmbd) * K[0] \
    + exp(2 * (b - 3 * l) * lmbd) \
    * (2 * b ** 2 * lmbd ** 2 - 2 * b * lmbd * (1 + 2 * l * lmbd)
    + 2 * lmbd * (l + l ** 2 * lmbd + 4 * a * K[2]) + K[1] ** 2
    + 4 * K[2] ** 2) \
    + exp(2 * (b - 2 * l) * lmbd) \
    * (2 * lmbd * (a - l - 2 * a ** 2 * lmbd - 8 * a * K[2])
    - K[1] ** 2 - 12 * K[2] ** 2)
 
 
def ank(n, k, a, b):
    return quad(lambda lmbd: f(lmbd, a, b) / lmbd
        * jn(n + 1, lmbd) * jn(k + 1, lmbd),
        0, Inf)[0]

 
def main():
    sz = 20
    amatrix = zeros((sz, sz))
    ls = linspace(1, 10, 20)
    for l in ls:
        a = -l / 2
        b = a + l
        for n in range(0, sz):
            for k in range(0, sz):
                amatrix[n, k] = ank(n, k, a, b)
        print(norm(amatrix))
 
if __name__ == '__main__':
    main()