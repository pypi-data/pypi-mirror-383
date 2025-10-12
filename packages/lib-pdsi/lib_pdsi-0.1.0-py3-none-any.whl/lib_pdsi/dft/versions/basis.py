import numpy as np

def basis_dft(x):

    N = len(x)
    X = np.zeros(N, dtype=complex)
    n = np.arange(N)

    for k in range(N):
        w_k = np.exp(-1j * 2 * np.pi/N * k * n)
        X[k] = w_k @ x

    return X