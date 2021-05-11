import numpy as np

class Wing:
    # Roskam method (not accurate because does not take into account density of material but good enough for comparison
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

    def get_weight(self):
        if self.config is None:
            return
        if self.config == 1 or self.config == 2:
            return self.wweight1*0.453592, self.wweight2*0.453592
        if self.config == 3:
            return self.wweight*0.453592

class Fuselage:
    # Roskam method (not accurate because does not take into account density of material but good enough for comparison
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

    def get_weight(self):
        if self.config is None:
            return
        if self.config in [1,2,3]:
            return self.fweight*0.453592

class LandingGear:

    def __init__(self, m = [], pos = []):
        self.m = np.array(m)
        self.pos = np.array(pos)

    def get_weight(self):
        return np.sum(self.m)

    def get_moment(self):
        return np.sum(self.m * 9.80665 * self.pos)

class Propulsion:

    def __init__(self, n_prop, m_prop = [], pos_prop = []):
        self.nprop = n_prop
        self.wprop = np.array(m_prop)*9.80665
        self.pos_prop = np.array(pos_prop)
        self.moment_prop = self.wprop*self.pos_prop

    def get_weight(self):
        return np.sum(self.wprop)

    def get_moment(self):
        return np.sum(self.wprop*self.pos_prop)

class Weight:

    def __init__(self, m_pax, wing, fuselage, landing_gear, propulsion, cargo_m, cargo_p, p_pax = []):
        self.w_pax = m_pax*9.80665
        # weights of components
        self.tot_pax_w = self.w_pax * 5
        self.wweight = wing.get_weight()
        self.fweight = fuselage.get_weight()
        self.lweight = landing_gear.get_weight()
        self.pweight = propulsion.get_pweight()
        self.cweight = cargo_m*9.80665

        #moments of components
        self.moment_pax = self.w_pax * np.array(p_pax)
        self.moment_w = wing.get_moment()
        self.moment_f = fuselage.get_moment()
        self.moment_l = landing_gear.get_moment()
        self.moment_p = propulsion.get_moment()
        self.moment_c = self.cweight * cargo_p

        #operational empty mass centre of gravity
        self.oem_cg = (self.moment_w + self.moment_f + self.moment_l + self.moment_p) \
        /(self.wweight + self.pweight + self.lweight + self.fweight)
        self.mtom_cg = (self.moment_w + self.moment_f + self.moment_l + self.moment_p + self.moment_pax + self.moment_c) \
        /(self.wweight + self.pweight + self.lweight + self.fweight + self.cweight)

        #masses
        self.oem = (self.moment_w + self.moment_f + self.moment_l + self.moment_p)
        self.mtom = (self.moment_w + self.moment_f + self.moment_l + self.moment_p + self.moment_pax + self.moment_c)


wing = Wing(2000, 10, 0, 3, 5, 2)
print(wing.get_weight())



