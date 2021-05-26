import numpy as np


class Noise:
    def __init__(self, P_br_cr, D, B, N_p_cr, N_p_h, rpm, sound_speed):
        """
        :param P_br: Engine power in kW [kW]
        :param D: Propeller diameter [m]
        :param B:  Number of blades [-]
        :param N_p: Number of propellers [-]
        :param sound_speed: Speed of sound [m/s]
        """
        self.P_cr = P_br_cr
        self.D = D
        self.B = B
        self.N_p_cr = N_p_cr
        self.N_p_h = N_p_h
        self.rpm = rpm
        self.M_t = np.pi*D*rpm/(sound_speed*60)

    def SPL_cr(self):
        return 83.4 + 15.3*np.log(self.P_cr) - 20*np.log(self.D) + 38.5*self.M_t - 3*(self.B-2) + 10*np.log(self.N_p_cr)

    def SPL_hover(self):
        return 1
