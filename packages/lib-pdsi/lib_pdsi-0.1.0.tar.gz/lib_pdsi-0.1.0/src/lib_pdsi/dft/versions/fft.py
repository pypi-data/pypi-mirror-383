import numpy as np

def fast_dft(x):
    """
    Calcula a DFT usando o algoritmo recursivo de Cooley-Tukey (FFT).
    """
    N = len(x)
    
    if N > 0 and not np.log2(N).is_integer():
        raise ValueError("Tamanho do sinal deve ser potência de 2")
    
    if N <= 1:
        return x

  
    Xe = fast_dft(x[0::2])
    Xo = fast_dft(x[1::2])
    
    k = np.arange(N//2)
    basis = np.exp(-2j * np.pi * k / N)
    
    term = basis * Xo
    first_half = Xe + term
    second_half = Xe - term
    
    return np.concatenate((first_half, second_half))