import numpy as np

def matrix_dft(x):

    N = len(x)
    n = np.arange(N)
    k = np.arange(N).reshape(N, 1) 
    
    W = np.exp(-1j * 2 * np.pi * k * n / N)
    
    X = W @ x

    return X