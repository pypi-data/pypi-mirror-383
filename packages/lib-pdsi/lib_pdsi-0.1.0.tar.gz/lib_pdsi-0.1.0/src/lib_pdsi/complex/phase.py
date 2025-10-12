import numpy as np

def complex_phase(z, version=3):
    if version == 1:
        phi = np.arctan(z.imag / z.real)
    if version == 2:
        phi = np.arctan2(z.imag, z.real)
    if version == 3:
        phi = np.angle(z)

    return phi