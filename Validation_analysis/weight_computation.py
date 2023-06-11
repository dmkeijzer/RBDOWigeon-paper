

class Wing:
    # Roskam method (not accurate because does not take into account density of material but good enough for comparison
    def __init__(self, mtom, S1, S2, n_ult, A_1, A_2):
        self.S1_ft, self.S2_ft, self.S1, self.S2 = S1 * 3.28084 ** 2, S2 * 3.28084 ** 2, S1, S2
        self.n_ult = n_ult
        self.A_1, self.A_2 = A_1, A_2
        self.mtow_lbs = 2.20462 * mtom
        self.wweight1 = 0.04674*((self.mtow_lbs/2)**0.397)*(self.S1_ft**0.36)*(self.n_ult**0.397)*(self.A_1**1.712)*0.453592
        self.wweight2 = 0.04674*((self.mtow_lbs/2)**0.397)*(self.S2_ft**0.36)*(self.n_ult**0.397)*(self.A_2**1.712)*0.453592

class Fuselage:
    # Roskam method (not accurate because does not take into account density of material but good enough for comparison
    def __init__(self, mtom, Pmax, lf, npax):
        self.mtow_lbs = 2.20462 * mtom
        self.lf_ft, self.lf = lf*3.28084, lf
        self.Pmax_ft = Pmax*3.28084
        self.npax = npax
        self.fweight_high = 14.86*(self.mtow_lbs**0.144)*((self.lf_ft/self.Pmax_ft)**0.778)*(self.lf_ft**0.383)*(self.npax**0.455)
        self.fweight_low = 0.04682*(self.mtow_lbs**0.692)*(self.Pmax_ft**0.379)*(self.lf_ft**0.590)
        self.fweight = (self.fweight_high + self.fweight_low)/2
        self.mass = self.fweight*0.453592

class LandingGear:
    def __init__(self, mtom):
        self.mass = 0.04*mtom