import numpy as np

M = np.array([[0, 1],
              [-1, 0]])

r = np.linalg.matrix_power(M, 3)


print(r)