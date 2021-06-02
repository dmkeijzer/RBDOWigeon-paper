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
        self.a_saf = airfoil[7]
        self.M = M
        self.S = S
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

    def CLmax_s(self, lh, h_ht, w, conf):
        ls = self.liftslope(lh, h_ht, w, conf)
        CLa = ls[0]
        deda = ls[3]
        CLmax1 = self.clmax
        alpha_s2 = round(((self.a_saf-self.a_0L)*(1-deda) +self.a_0L)*4)/4
        CLmax2 = airfoil_datapoint("CL", "Stall",alpha_s2)
        CLmax = self.s1*0.9*CLmax1 +self.s2*0.9*CLmax2
        self.a_s = CLmax/CLa + self.a_0L
        return CLmax, CLmax1, CLmax2, self.a_s

    def post_stall_lift_drag(self, lh, h_ht, w, conf, tc, CDs_W, CDs_f, Afus):
        #Wing
        stall = self.CLmax_s( lh, h_ht, w, conf)
        CLs = stall[0]
        a_s = self.a_s*np.pi/180
        A1 = 0.5*(1.1 + 0.018* self.AR_i)
        A2 = (CLs - 2*A1*np.sin(a_s)*np.cos(a_s))*(np.sin(a_s)/(np.cos(a_s)**2))
        CDmax = (1 + 0.065*self.AR_i)/(0.9 + tc)
        B2 = (CDs_W - CDmax * np.sin(a_s))/np.cos(a_s)

        alpha_ps = (np.pi/180)*np.arange(round(a_s)+1, 90, 1)
        CL_ps = A1*np.sin(2*alpha_ps)+A2*((np.cos(alpha_ps)**2)/np.sin(alpha_ps))
        CD_ps = CDmax*np.sin(alpha_ps)+ B2 * np.cos(alpha_ps)

        # Fuselage
        CDmax_f = 1.18*Afus/self.S # https://sv.20file.org/up1/916_0.pdf Drag coefficient of a cylinder
        B2_f = (CDs_f - CDmax_f * np.sin(a_s)) / np.cos(a_s)
        CD_ps_f = CDmax_f * np.sin(alpha_ps) + B2_f * np.cos(alpha_ps)
        return alpha_ps, CL_ps, CD_ps, CD_ps_f

    def CLa(self, lh, h_ht, w, conf, tc, CDs_W, CDs_f):

        poststall = self.post_stall_lift_drag( lh, h_ht, w, conf, tc, CDs_W, CDs_f)
        CLa = self.liftslope(lh, h_ht, w, conf)

        alpha = np.arange(-5,self.a_s,0.25)
        CL = CLa*(alpha - self.a_0L)
        np.append(alpha,poststall[0])
        np.append(CL,poststall[1])
        return alpha, CL

