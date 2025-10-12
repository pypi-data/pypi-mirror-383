import numpy as np

def complex_magnitude(z, version=2):
    if version == 1:
        return np.sqrt(z.real**2 + z.imag**2)
    if version == 2:
        return np.abs(z)