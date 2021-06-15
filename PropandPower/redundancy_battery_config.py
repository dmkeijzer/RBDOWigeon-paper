import numpy as np

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

class redundancy_power:
    def __init__(self, V_motor, E_tot, P_in_motor, V_cell, C_cell, n_mot, n_bat_mot):
        """
        :param V_motor:
        :param E_tot:
        :param P_in_moter:
        :param V_cell:
        :param C_cell:
        :param n_mot:
        :param n_bat_mot:
        """
        self.V_motor = V_motor
        self.E_tot = E_tot
        self.P_in_motor = P_in_motor
        self.V_cell = V_cell
        self.C_cell = C_cell
        self.E_cell = V_cell * C_cell
        self.n_mot = n_mot
        self.n_bat_mot = n_bat_mot

    def N_cells(self):
        return int(np.ceil(self.E_tot / self.E_cell * 1000))

    def N_ser(self):
        return int(np.ceil(self.V_motor / self.V_cell))

    def N_par(self):
        return int(np.ceil(self.N_cells() / self.N_ser()))

    def N_par_new(self):
        return closestNumber(self.N_par(), self.n_mot*self.n_bat_mot)

    def N_cells_new(self):
        return self.N_ser()*self.N_par_new()
