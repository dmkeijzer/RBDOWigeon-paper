import numpy as np
from scipy.linalg import null_space
from matplotlib import pyplot as plt
from matplotlib import colors as mc
from Aero_tools import ISA
class VT_sizing:
    def __init__(self,W,h,lfus,hfus,wfus,xcg,V0,Vstall,M0,CD0,theta0,CLfwd,CLrear,
                 CLafwd,CLarear, Cmacfwd,Cmacrear,
                 Sfwd,Srear,Afwd,Arear,Lambda_c2_fwd,Lambda_c2_rear,cfwd,crear,bfwd,brear,efwd,erear,taper):
        self.W = W         # Weight [N]
        self.h = h     # Height [m]
        Aero = ISA(self.h)
        self.rho = Aero.density()
        self.mu = Aero.viscosity_dyn()
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
        self.taper = taper # Wing taper ratio [-]
        self.CLfwd,self.CLrear  = CLfwd,CLrear # DESIGN FOR CRUISE Lift coefficients [-]
        self.Afwd, self.Arear = Afwd, Arear # Aspect ratio of both wings [-]
        self.Sweepc2fwd = Lambda_c2_fwd # Sweep at c/2 [rad]
        self.Sweepc2rear = Lambda_c2_rear # Sweep at c/2 [rad]
        self.Sweepc4fwd = self.Sweep(Afwd,self.Sweepc2fwd,25,50)
        self.Sweepc4rear = self.Sweep(Arear, self.Sweepc2rear, 25, 50)
        self.th0 = theta0  # Initial pitch angle [rad]
        self.V0 = V0       # Initial speed [m/s]
        self.M0 = M0       # Initial mach number [-]
        self.Re = self.rho*self.V0*self.lfus/self.mu
        self.CLafwd, self.CLarear = CLafwd, CLarear # Wing lift curve slopes for both wings [1/rad]
        self.Cmacfwd, self.Cmacrear = Cmacfwd,Cmacrear
        self.CD0 = CD0 # C_D_0 of forward wing
        self.xacfwd = 0.25*self.cfwd
        self.xacrear = self.lfus - (1 - 0.25) * self.crear
        self.de_da = self.deps_da(self.Sweepc4fwd,self.bfwd,self.lh(),self.hfus,self.Afwd,self.CLafwd)
        self.taper_v = 0.4
        self.Vs = Vstall
        self.Vmc = 1.2*self.Vs
        self.xcg = xcg
        self.c = self.Sfwd/self.S*self.cfwd+self.Srear/self.S*self.crear
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
    def initial_VT(self,lv,VT = 0.04):
        """
        Inputs:
        AIRFOIL USED: 0012
        :param lv:
        :param VT:
        :return:
        """
        Sv = max(self.bfwd,self.brear)*self.S*VT/lv
        ARv = 1.25
        bv = np.sqrt(ARv*Sv)
        C_v = Sv/bv
        C_vr = 3/2*C_v*(1+self.taper_v)/(1+self.taper_v+self.taper_v**2)
        C_vt = self.taper_v*C_vr
        Sweep_v_c2 = 15*np.pi/180
        return Sv,ARv,bv,C_v,Sweep_v_c2,C_vr,C_vt

    def tau(self,Cr,Cv):
        """
        Inputs:
        :param Cr: MAC of rudder [m]
        :param Cv: MAC vertical tail [m]
        :return: rudder effectiveness [-]
        """
        return 1.129*(Cr/Cv)**0.4044 - 0.1772

    def VT_controllability(self,nE,Tt0,yE,lv):
        """
        Inputs:
        :param nE: Number of engines [-]
        :param Tt0: Take-off thrust [N]
        :param yE: Largest moment arm [m]
        :return: Required vertical tail area [m^2] for controllability
        """
        N_E = Tt0/nE*yE # Asymmetric yaw moment [Nm]
        N_D = 0.25*N_E # component due to drag [Nm]
        N_total = N_E + N_D
        Sr_Sv = 0.2
        br_bv = 0.85
        Cr_Cv = 0.25
        dr_max = 25*np.pi/180
        C_rudder = self.initial_VT(lv)[3]*Cr_Cv
        tau_r = self.tau(C_rudder,self.initial_VT(lv)[3])
        CLa_v = self.C_L_a(self.initial_VT(lv)[1],self.initial_VT(lv)[4])
        Vv_V = 1
        Sv = N_total/(0.5*self.rho*self.Vmc**2*CLa_v*lv*Vv_V**2*tau_r*br_bv*dr_max)
        return Sv

    def VT_stability(self,lv):
        kn = 0.01*(0.27*self.xcg/self.lfus-0.168*np.log(self.lfus/self.wfus)+0.416)-0.0005
        kR = 0.46*np.log10(self.Re/10**6)+1
        Cnb_fus = -360/(2*np.pi)*kn*kR*self.lfus**2*self.wfus/(self.S*max(self.brear,self.bfwd))
        a = self.lfus/2
        b = self.wfus/2
        V = 2*np.pi/4*b**2*(self.lfus/2-(self.lfus/2)**3/(3*a**2))
        Cnb_fus = -2*V/(self.S*max(self.bfwd,self.brear))
        Cnb_w_fwd = self.CLfwd**2*(1/(4*np.pi*self.Afwd)-
                                   (np.tan(self.Sweepc2fwd)/(np.pi*self.Afwd+4*np.cos(self.Sweepc2fwd)))*
                                   (np.cos(self.Sweepc2fwd)-self.Afwd/2-self.Afwd**2/(8*np.cos(self.Sweepc2fwd))-
                                    6*(self.xacfwd-self.xcg)*np.sin(self.Sweepc2fwd)/(self.Afwd*self.c)))
        Cnb_w_rear = self.CLrear**2*(1/(4*np.pi*self.Arear)-
                                   (np.tan(self.Sweepc2rear)/(np.pi*self.Arear+4*np.cos(self.Sweepc2rear)))*
                                   (np.cos(self.Sweepc2rear)-self.Afwd/2-self.Arear**2/(8*np.cos(self.Sweepc2rear))-
                                    6*(self.xacrear-self.xcg)*np.sin(self.Sweepc2rear)/(self.Arear*self.c)))
        CYb_v = -self.C_L_a(self.initial_VT(lv)[1],self.initial_VT(lv)[4])

        Cnb = 0.06
        Sv = self.S*(Cnb-Cnb_fus+Cnb_w_fwd+Cnb_w_rear)/(-CYb_v)*max(self.brear,self.bfwd)/lv
        return Sv

    def min_Sv(self,nE,Tt0,yE,lv):
        Sv = max(self.VT_stability(lv),self.VT_controllability(nE,Tt0,yE,lv))
        return Sv

