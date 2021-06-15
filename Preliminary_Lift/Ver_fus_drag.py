import numpy as np

def fus_drag(Re, M, S_n, S_c, S_t, S):
    CDfp = 0.455 / (((np.log10(Re)) ** 2.58) * (1 + 0.144 * M * M) ** 0.58)

    K_n = 1.93
    K_c = 1.6
    K_t = 1.05

    return (K_n*S_n + K_c*S_c + K_t*S_t)*CDfp*(1/S)


print(fus_drag(4000000, 0.2, 17))
