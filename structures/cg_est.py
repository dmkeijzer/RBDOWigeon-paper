""" this file will provide an estimation of the OEM centre of gravity position
both methods are taken from Roskam Part V: Component weight estimation - the cessna method specifically
this is not very accurate because it does not take into account the material used, but is
ok for trade-off comparison between the configurations"""

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

class Fuselage:

    def __init__(self, mtom, Pmax, lf, npax, config = None):
        self.config = config
        self.mtow_lbs = 2.20462 * mtom * 9.80665
        self.lf_ft = lf*3.28084
        self.Pmax_ft = Pmax*3.28084
        if self.config is not None and self.config in [1, 2, 3]:
            if self.config == 1 or config == 2:
                self.fweight_high = 14.86*(self.mtow_lbs**0.144)*((self.lf_ft/self.Pmax_ft)**0.778)*(self.lf_ft**0.383)\
                *(npax**0.455)
                self.fweight_low = 0.004682*(self.mtow_lbs**0.692)*(self.Pmax_ft**0.379)*(self.lf_ft**0.590)
                self.fweight = (self.fweight_high + self.fweight_low)/2
            if self.config == 3:
                self.fweight = 0.004682 * (self.mtow_lbs ** 0.692) * (self.Pmax_ft ** 0.379) * (self.lf_ft ** 0.590)
                # for high wing uncomment the next line
                # self.fweight_high = 14.86 * (self.mtow_lbs ** 0.144) * ((self.lf_ft / self.Pmax_ft) ** 0.778)\
                #                     * (self.lf_ft ** 0.383) * (npax ** 0.455)
        else:
            print("Please select configuration from 1 to 3")

    def get_fweight(self):
        if self.config is None:
            return
        if self.config in [1,2,3]:
            return self.fweight*0.453592


wing = Wing(2000, 10, 0, 3, 5, 2)
print(wing.get_wweight())



