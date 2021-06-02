import numpy as np
from scipy.linalg import null_space
from matplotlib import pyplot as plt
from matplotlib import colors as mc
from Aero_tools import ISA
class Control_surface:
    def __init__(self,V0,Vstall,CLfwd,CLrear,
                 CLafwd,CLarear, Clafwd,Clarear,Cd0fwd,Cd0rear,Cmacfwd,Cmacrear,
                 Sfwd,Srear,Afwd,Arear,cfwd,crear,bfwd,brear,taper):
        # self.W = W         # Weight [N]
        # self.h = h     # Height [m]
        # Aero = ISA(self.h)
        # self.rho = Aero.density()
        # self.mu = Aero.viscosity_dyn()
        # self.lfus = lfus # Length of the fuselage
        # self.hsus = hfus # Height of the fuselage [m]
        # self.wfus = wfus # Maximum width of the fuselage [m]
        self.Srear = Srear # Rear wing area [m^2]
        self.Sfwd = Sfwd   # Forward wing area [m^2]
        self.S = Srear+Sfwd # Aircraft wing area [m^2]
        self.cfwd = cfwd         # Average chord [m]
        self.crear = crear  # Average chord [m]
        self.bfwd = bfwd         # Wing span [m]
        self.brear = brear # Wing span [m]
        self.taper = taper # Wing taper ratio [-]
        self.Clafwd,self.Clarear = Clafwd,Clarear # Airfoil lift curve [1/rad]
        self.Cd0fwd,self.Cd0rear = Cd0fwd,Cd0rear # Airfoil zero drag coefficient [-]
        self.CLfwd,self.CLrear  = CLfwd,CLrear # DESIGN FOR CRUISE Lift coefficients [-]
        self.Afwd, self.Arear = Afwd, Arear # Aspect ratio of both wings [-]
        # self.Sweepc2fwd = Lambda_c2_fwd # Sweep at c/2 [rad]
        # self.Sweepc2rear = Lambda_c2_rear # Sweep at c/2 [rad]
        # self.Sweepc4fwd = self.Sweep(Afwd,self.Sweepc2fwd,25,50)
        # self.Sweepc4rear = self.Sweep(Arear, self.Sweepc2rear, 25, 50)
        # self.th0 = theta0  # Initial pitch angle [rad]
        self.V0 = V0       # Initial speed [m/s]
        # self.M0 = M0       # Initial mach number [-]
        # self.Re = self.rho*self.V0*self.lfus/self.mu
        self.CLafwd, self.CLarear = CLafwd, CLarear # Wing lift curve slopes for both wings [1/rad]
        self.Cmacfwd, self.Cmacrear = Cmacfwd,Cmacrear
        # self.CD0 = CD0 # C_D_0 of forward wing
        self.xacfwd = 0.25*self.cfwd
        self.xacrear = self.lfus - (1 - 0.25) * self.crear
        # self.de_da = self.deps_da(self.Sweepc4fwd,self.bfwd,self.lh(),self.hfus,self.Afwd,self.CLafwd)
        self.taper_v = 0.4
        self.Vs = Vstall # Stall speed [m/s]
        self.Vmc = 1.2*self.Vs # Mimum controllable speed [m/s]
        # self.xcg = xcg
        self.c = self.Sfwd/self.S*self.cfwd+self.Srear/self.S*self.crear

    def Sweep(self,AR,Sweepm,n,m):
        """
        Inputs
        :param AR: Aspect Ratio of VT
        :param Sweepm: Sweep at mth chord [rad]
        :param n: (example quarter chord: n =25)
        :param m: mth chord (example half chord: m=50)
        :return: Sweep at nth chord [rad]
        """
        tanSweep_m = np.tan(Sweepm)
        tanSweep_n = tanSweep_m -4/(AR*4)*(n-m)/100*(1-self.taper)/(1+self.taper)
        return np.arctan(tanSweep_n)

    def tau_a(self,Sa_S):
        """
        Inputs:
        :param Sa_S: Aileron surface to wing ratio [-]
        :return: Aileron Effectiveness [-]
        """
        x = Sa_S
        tau_a = -6.624*x**4+12.07*x**3-8.292*x**2+3.295*x+0.004942
        return tau_a

    def Clda(self,b2):
        """
        Input:
        :param b2: Outer distance of the aileron [m]
        :return: Control derivative C_l_da [1/rad]
        """
        b1 = 0.7*self.bfwd/2
        c_r = self.cfwd*3/2*(1+self.taper)/(1+self.taper+self.taper**2)
        Sa_S = 0.075
        Clda = self.CLafwd*self.tau_a(Sa_S)*c_r/(self.Sfwd*self.bfwd)*\
               (0.5*(b2**2-b1**2) + 2*(self.taper-1)/(3*self.bfwd)*(b2**3-b1**3))
        return Clda

    def Clp(self):
        c_r_fwd = self.cfwd * 3 / 2 * (1 + self.taper) / (1 + self.taper + self.taper ** 2)
        c_r_rear =  self.crear*3/2*(1+self.taper)/(1+self.taper+self.taper**2)
        Clp_fwd =-(self.Clafwd+self.Cd0fwd)*c_r_fwd*self.bfwd/(24*self.Sfwd)
        Clp_rear = -(self.Clarear + self.Cd0rear) * c_r_rear * self.brear/(24 * self.Srear)
        Clp = Clp_fwd+Clp_rear
        return Clp

    def plotting(self,b2):
        da_max = 30*np.pi/180
        dphi_dt = 60*np.pi/180
        minClda = -(dphi_dt)/1.3*self.Clp()*max(self.bfwd,self.brear)/(2*self.Vmc*da_max)
        minClda = np.ones(len(b2))*minClda
        Clda_array = self.Clda(b2)
        plt.plot(b2,minClda,label=r"Minimum value required $C_{l_{\delta_a}}$")
        plt.plot(b2,Clda_array,label=r"$C_{l_{\delta_a}}$")
        plt.xlabel(r"$b_2 [m]$",fontsize=14)
        plt.ylabel(r"$C_{l_{\delta_a}}$")
        plt.legend()
        plt.show()


