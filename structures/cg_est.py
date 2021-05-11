""" this file will provide an estimation of the OEM centre of gravity position"""

import numpy

class Wing:

    def __init__(self, mtom, S1, S2, n_ult, A, config = None):
        self.config = config
        self.S1_ft, self.S2_ft = S1 * 3.28084 ** 2, S2 * 3.28084 ** 2
        self.mtow_lbs = 2.20462 * mtom * 9.80665
        if self.config is not None and self.config in [1,2,3]:
            if self.config == 1:
                self.wweight1 = 0.04674*(self.mtow_lbs**0.397)*(self.S1_ft**0.36)*(n_ult**0.397)*(A**1.712)
                self.wweight2 = 0.04674*(self.mtow_lbs**0.397)*(self.S2_ft**0.36)*(n_ult**0.397)*(A**1.712)
            if self.config == 2:
                self.wweight1 = 0.04674 * (self.mtow_lbs ** 0.397) * (self.S1_ft ** 0.36) * (n_ult ** 0.397) * (A ** 1.712)
                self.wweight2 = 0.04674 * (self.mtow_lbs ** 0.397) * (self.S2_ft ** 0.36) * (n_ult ** 0.397) * (A ** 1.712)
            if self.config == 3:
                self.wweight = 0.04674 * (self.mtow_lbs ** 0.397) * (self.S1_ft ** 0.36) * (n_ult ** 0.397) * (A ** 1.712)
        else:
            print("Please select configuration from 1 to 3")

    def get_wweight(self):
        if self.config is None:
            return
        if self.config == 1 or self.config == 2:
            return self.wweight1*0.453592, self.wweight2*0.453592
        if self.config == 3:
            return self.wweight*0.453592

wing = Wing(2000, 10, 0, 3, 5, 2)
print(wing.get_wweight())



