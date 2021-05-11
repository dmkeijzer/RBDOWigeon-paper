""" this file will provide an estimation of the OEM centre of gravity position"""

import numpy

class Wing:

    def __init__(self, mtom, S1, S2, n_ult, A, config = None):
        if config is None or config not in [1,2,3]:
            raise ("Please specify the configuration")
        self.S1_ft, self.S2_ft = S1*3.28084**2, S2*3.28084**2
        self.mtow_lbs = 2.20462*mtom*9.80665
        if config == 1:
            self.wweight1 = 0.04674*(self.mtow_lbs**0.397)*(S1_ft**0.36)*(n_ult**0.397)*(A**1.712)
            self.wweight2 = 0.04674*(self.mtow_lbs**0.397)*(S2_ft**0.36)*(n_ult**0.397)*(A**1.712)
        if config == 2:
            self.wweight1 = 0.04674 * (self.mtow_lbs ** 0.397) * (S1_ft ** 0.36) * (n_ult ** 0.397) * (A ** 1.712)
            self.wweight2 = 0.04674 * (self.mtow_lbs ** 0.397) * (S2_ft ** 0.36) * (n_ult ** 0.397) * (A ** 1.712)
        if config == 3:
            self.wweight = 0.04674 * (self.mtow_lbs ** 0.397) * (S1_ft ** 0.36) * (n_ult ** 0.397) * (A ** 1.712)

    def get_wweight(self):
        if config == 1 or config == 2:
            return self.wweight1, self.wweight2
        if config == 3:
            return self.wweight




