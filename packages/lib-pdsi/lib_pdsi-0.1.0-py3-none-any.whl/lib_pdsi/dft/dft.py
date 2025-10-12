import numpy as np

from .versions.signal import signal_dft
from .versions.basis import basis_dft
from .versions.mtx import matrix_dft
from .versions.fft import fast_dft


def dft(x, version="fft"):
    if version == "signal":
        return signal_dft(x)
    
    if version == "basis":
        return basis_dft(x)
    
    if version == "matrix":
        return matrix_dft(x)
    
    if version == "fft":
        return fast_dft(x)
    
    if version == "numpy":
        return np.fft.fft(x)
    
