import numpy as np


class Noise:
    def __init__(self, P_br, D, B, N_p, rpm, sound_speed):
        """
        :param P_br: Engine power in kW [kW]
        :param D: Propeller diameter [m]
        :param B:  Number of blades [-]
        :param N_p: Number of propellers [-]
        :param sound_speed: Speed of sound [m/s]
        """
        self.P = P_br
        self.D = D
        self.B = B
        self.N_p = N_p
        self.rpm = rpm
        self.M_t = np.pi*D*rpm/(sound_speed*60)

    def SPL_prop_max(self):
        return 83.4 + 15.3*np.log(self.P) - 20*np.log(self.D) + 38.5*self.M_t - 3*(self.B-2) + 10*np.log(self.N_p)

    def SPL_hover(self):
        return 1
