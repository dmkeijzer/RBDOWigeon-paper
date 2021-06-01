import numpy as np
from Preliminary_Lift.Airfoil_analysis import airfoil_stats, airfoil_datapoint
from stab_and_ctrl.cg_limits_horizontal_flight import deps_da

class wing_design:

    def __init__(self, AR, s1, sweepc41, s2, sweepc42, M, S):
        self.AR_b = AR
        self.s1 = s1
        self.S1 = s1 * S
        self.sweepc41 = sweepc41
        self.s2 = s2
        self.S2 = s2 *S
        self.sweepc42= sweepc42
        airfoil = airfoil_stats()
        self.clmax = airfoil[0]
        self.Cl_Cdmin = airfoil[2]
        self.Clalpha = airfoil[4]* 180/np.pi
        self.a_0L = airfoil[8]
        self.M = M
    def taper_opt(self):
        return 0.45 * np.exp(-0.036 * self.sweepc41), 0.45 * np.exp(-0.036 * self.sweepc42)  # Eq. 7.4 Conceptual Design of a Medium Range Box Wing Aircraft

    def wing_planform_double(self):
        # Wing 1
        self.taper1 = self.taper_opt()[0]
        self.taper2 = self.taper_opt()[1]
        b1 = np.sqrt(2 * self.AR_b * self.S1)
        c_r1 = 2 * self.S1 / ((1 + self.taper1) * b1)
        c_t1 = self.taper1 * c_r1
        c_MAC1 = (2 / 3) * c_r1 * ((1 + self.taper1 + self.taper1 ** 2) / (1 + self.taper1))
        y_MAC1 = (b1 / 6) * ((1 + 2 * self.taper1) / (1 + self.taper1))
        tan_sweep_LE1 = 0.25 * (2 * c_r1 / b1) * (1 - self.taper1) + np.tan(self.sweepc41)

        X_LEMAC1 = y_MAC1 * tan_sweep_LE1
        wing1 = [b1, c_r1, c_t1, c_MAC1, y_MAC1, X_LEMAC1]

        # Wing 2

        b2 = np.sqrt(2 * self.AR_b * self.S2)
        c_r2 = 2 * self.S2 / ((1 + self.taper2) * b2)
        c_t2 = self.taper2 * c_r2
        c_MAC2 = (2 / 3) * c_r2 * ((1 + self.taper2 + self.taper2 ** 2) / (1 + self.taper2))
        y_MAC2 = (b2 / 6) * ((1 + 2 * self.taper2) / (1 + self.taper2))
        tan_sweep_LE2 = 0.25 * (2 * c_r2 / b2) * (1 - self.taper2) + np.tan(self.sweepc42)

        X_LEMAC2 = y_MAC2 * tan_sweep_LE2
        wing2 = [b2, c_r2, c_t2, c_MAC2, y_MAC2, X_LEMAC2]

        return wing1, wing2

    def sweep_atx(self, x):
        wg = self.wing_planform_double()
        b1 = wg[0][0]
        c_r1 =  wg[0][1]
        b2 = wg[1][0]
        c_r2 = wg[1][1]
        tan_sweep_LE1 = 0.25 * (2 * c_r1 / b1) * (1 - self.taper1) + np.tan(self.sweepc41)
        sweep1 = np.arctan(tan_sweep_LE1- x * (2 * c_r1 / b1) * (1 - self.taper1))
        tan_sweep_LE2 = 0.25 * (2 * c_r2 / b2) * (1 - self.taper2) + np.tan(self.sweepc42)
        sweep2 = np.arctan(tan_sweep_LE2 - x * (2 * c_r2 / b2) * (1 - self.taper2))
        return sweep1, sweep2

    def liftslope(self, lh, h_ht, w, conf):
        beta = np.sqrt(1 - self.M ** 2)
        SW = np.tan(self.sweep_atx(0.5))
        self.AR_i = 2*self.AR_b
        slope1 = self.Clalpha * (self.AR_i / (2 + np.sqrt(4 + ((self.AR_i * beta / 0.95) ** 2) * ((1 + SW ** 2) / (beta ** 2)))))
        wg =  self.wing_planform_double()
        deda = deps_da(self.sweepc41, wg[0][0],lh,h_ht, self.AR_i,slope1, conf)
        wfi = 1 + 0.025*(w/wg[0][0]) - 0.25*(w/wg[0][0])  # wing fuselage interaction factor: effect of fuselage diameter on aerodynamic characteristics for straightwing at low and high aspect ratio

        slope2 = slope1 * (1 - deda)
        slope_tot = wfi*(slope1 * self.s1 + slope2 * self.s2)
        return slope_tot, slope1* wfi, slope2*wfi, deda

    #def CLmax(self):
        #Clmax1 = self.clmax
        #alpha_s2 =
        #Clmax2 = airfoil_datapoint("CL", "Stall",)