import numpy as np
from scipy.linalg import null_space
from matplotlib import pyplot as plt
from matplotlib import colors as mc

class Wing_placement_sizing:
    def __init__(self,W,h,lfus,hfus,wfus,V0,M0,CD0,theta0,
                 CLfwd,CLrear,CLafwd,CLarear, Cmacfwd,Cmacrear,
                 Sfwd,Srear,Afwd,Arear,Gamma,Lambda_c2_fwd,Lambda_c2_rear,cfwd,crear,bfwd,brear,efwd,erear,taper):
        self.W = W         # Weight [N]
        self.h = h     # Height [m]
        self.lfus = lfus # Length of the fuselage
        self.hsus = hfus # Height of the fuselage [m]
        self.wfus = wfus # Width of the fuselage [m]
        self.Srear = Srear # Rear wing area [m^2]
        self.Sfwd = Sfwd   # Forward wing area [m^2]
        self.S = Srear+Sfwd # Aircraft wing area [m^2]
        self.cfwd = cfwd         # Average chord [m]
        self.crear = crear  # Average chord [m]
        self.bfwd = bfwd         # Wing span [m]
        self.brear = brear # Wing span [m]
        self.efwd, self.erear = efwd,erear
        self.taper = taper
        self.Afwd, self.Arear = Afwd, Arear # Aspect ratio of both wings [-]
        self.Sweepc2fwd = Lambda_c2_fwd # Sweep at c/2 [rad]
        self.Sweepc2rear = Lambda_c2_rear # Sweep at c/2 [rad]
        self.Sweepc4fwd = self.Sweep(Afwd,self.Sweepc2fwd,25,50)
        self.Sweepc4rear = self.Sweep(Arear, self.Sweepc2rear, 25, 50)
        self.th0 = theta0  # Initial pitch angle [rad]
        self.V0 = V0       # Initial speed [m/s]
        self.M0 = M0       # Initial mach number [-]
        self.Gamma_fwd = Gamma # Forward wing dihedral [rad]
        self.CLfwd = CLfwd # Forward lift coefficient [-]
        self.CLrear = CLrear # Rear lift coefficient [-]
        self.CLafwd, self.CLarear = CLafwd, CLarear # Wing lift curve slopes for both wings [1/rad]
        self.Cmacfwd, self.Cmacrear = Cmacfwd,Cmacrear
        self.CD0 = CD0 # C_D_0 of forward wing
        self.xacfwd = 0.25*self.cfwd
        self.xacrear = self.lfus - (1 - 0.25) * self.crear
        self.de_da = self.deps_da(self.Sweepc4fwd,self.bfwd,self.lh(),self.hfus,self.Afwd,self.CLafwd)

    def lh(self):
        return abs(self.xacfwd - self.xacrear)

    def deps_da(self,Lambda_quarter_chord, b, lh, h_ht, A, CLaw):
        """
        Inputs:
        :param Lambda_quarter_chord: Sweep Angle at c/4 [RAD]
        :param lh: distance between ac_w1 with ac_w2 (horizontal)
        :param h_ht: distance between ac_w1 with ac_w2 (vertical)
        :param A: Aspect Ratio of wing
        :param CLaw: Wing Lift curve slope
        :return: de/dalpha
        """
        r = lh * 2 / b
        mtv = h_ht * 2 / b
        Keps = (0.1124 + 0.1265 * Lambda_quarter_chord + 0.1766 * Lambda_quarter_chord ** 2) / r ** 2 + 0.1024 / r + 2
        Keps0 = 0.1124 / r ** 2 + 0.1024 / r + 2
        v = 1 + (r ** 2 / (r ** 2 + 0.7915 + 5.0734 * mtv ** 2) ** (0.3113))
        de_da = Keps / Keps0 * CLaw / (np.pi * A) * (
                r / (r ** 2 + mtv ** 2) * 0.4876 / (np.sqrt(r ** 2 + 0.6319 + mtv ** 2)) + v * (
                1 - np.sqrt(mtv ** 2 / (1 + mtv ** 2))))
        phi = np.arcsin(mtv/r)
        # print("Configuration %.0f de/da = %.4f "%(conf,de_da))
        return de_da

    def Sweep(self,AR,Sweepm,n,m):
        """
        Inputs
        :param AR: Aspect Ratio
        :param Sweepm: Sweep at mth chord [rad]
        :param n: (example quarter chord: n =25)
        :param m: mth chord (example half chord: m=50)
        :return: Sweep at nth chord [rad]
        """
        tanSweep_m = np.tan(Sweepm)
        tanSweep_n = tanSweep_m -4/(AR)*(n-m)/100*(1-self.taper)/(1+self.taper)
        return np.arctan(tanSweep_n)

    def C_L_a(self,A, Lambda_half, eta=0.95):
        """
        Inputs:
        :param M: Mach number
        :param b: wing span
        :param S: wing area
        :param Lambda_half: Sweep angle at 0.5*chord
        :param eta: =0.95
        :return: Lift curve slope for tail AND wing using DATCOM method
        """
        M= self.M0
        beta = np.sqrt(1 - M ** 2)
        value = 2 * np.pi * A / (2 + np.sqrt(4 + ((A * beta / eta) ** 2) * (1 + (np.tan(Lambda_half) / beta) ** 2)))
        return value

    def Sr_Sfwd(self, Xcg, elevator, d):
        """
        Inputs:
        :param Xcg: Array of cg positions from 1 to the length of the fuselage
        :param elevator: Elevator effectiveness factor to CL_fwd
        :param d: Alterning parameter d for position change of rear wing
        :return: S_fwd/S_rear array for both stability and controllability
        """
        CLfwd = self.CLfwd * elevator
        CDfwd = self.CD0 + self.CLfwd ** 2 / (np.pi * self.Afwd * self.efwd)
        CDrear = self.CD0 + self.CLrear ** 2 / (np.pi * self.Arear * self.erear)
        c = self.Sfwd / (self.Sfwd + self.Srear) * self.cfwd + self.Srear / (self.Srear + self.Sfwd) * self.crear
        # CDafwd = 2*CLafwd*CLfwd/(np.pi*Afwd*e)
        # CDarear = 2*CLarear*CLrear/(np.pi*Afwd*e)
        deda = self.de_da
        # print("de/da = ",deda)
        SrSfwd_stab = self.CLafwd * (Xcg - self.xacfwd) / (self.CLarear * (1 - deda) * (self.xacrear - d - Xcg))
        SrSfwd_control = (-self.Cmacfwd * self.cfwd + CDfwd * self.hfus / 2 - CLfwd * (Xcg - self.xacfwd) / (
                        CDrear * self.hfus / 2 - self.CLrear * (self.xacrear -d- Xcg) + self.Cmacrear * self.crear))
        return SrSfwd_stab ** -1, SrSfwd_control ** -1

    def plotting(self,Xcg,elevator,d):
        SrSfwd_stability = self.Sr_Sfwd(Xcg,elevator,d)[0]
        SrSfwd_control = self.Sr_Sfwd(Xcg, elevator, d)[1]
        plt.plot(Xcg,SrSfwd_stability,label="Neutral Stability Line")
        plt.plot(Xcg,SrSfwd_control,label="Controllability Line")
        plt.xlabel(r"$x_{cg}$ [m]",fontsize=14)
        plt.ylabel(r"$\cfrac{S_{fwd}}{S_{rear}}$ [-]",fontsize=14)
        plt.legend()
        plt.show()


