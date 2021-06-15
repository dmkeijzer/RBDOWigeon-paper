# from Midterm2_for_convergence.main_remidterm import energy
import numpy as np
from functools import reduce
from math import sqrt

# Characteristics from the plane
V_motor = 500 # V
E_tot = 311121.1005976536 # kWh
P_in_motor = 270000 # W

# Cell characteristics
V_cell = 3.4 # V
C_cell = 250 # Ah
E_cell = V_cell * C_cell # Wh

# inputs
n_mot = 12 # Number of motors in aircraft
n_bat_mot = 2 # Number of batteries per motor

def factors(n):
    step = 2 if n % 2 else 1
    return set(reduce(list.__add__,
                      ([i, n // i] for i in range(1, int(sqrt(n)) + 1, step) if n % i == 0)))

def closestNumber(n, m):
    # Find the quotient
    q = int(n / m)

    # 1st possible closest number
    n1 = m * q

    # 2nd possible closest number
    if ((n * m) > 0):
        n2 = (m * (q + 1))
    else:
        n2 = (m * (q - 1))

    # if true, then n1 is the required closest number
    if n1 > n:
        return n1
    else:
        return n2

N_cells = int(np.ceil(E_tot / E_cell * 1000))
print("Number of cells for required energy/power:", N_cells)

N_ser = int(np.ceil(V_motor / V_cell))
print("Number of cells in series for required voltage:", N_ser)

N_par = int(np.ceil(N_cells/N_ser))
print("Number of modules in parallel when using", N_ser, "cells in series:", N_par)

N_par_new = closestNumber(N_par,n_mot*n_bat_mot)
print("Number of modules for ", n_mot*n_bat_mot, "batteries:", N_par_new)

N_cells_new = N_ser*N_par_new
print("Number of battery cells when multiplying parallel and series:", N_cells_new)
print("This is", N_cells_new - N_cells, "cells more than needed for energy")
print("This is a ", np.round(((N_cells_new-N_cells)/N_cells*100),2), "% increase")



