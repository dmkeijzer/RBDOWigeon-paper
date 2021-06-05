import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors as mc

class Elevator_sizing:
    def __init__(self,W,h,xcg,lfus,hfus,wfus,V0,Vstall,CD0,theta0,CLfwd,CLrear,
                 CLafwd,CLarear, Cmacfwd,Cmacrear,
                 Sfwd,Srear,Afwd,Arear,Lambda_c4_fwd,Lambda_c4_rear,cfwd,crear,bfwd,brear,taper,dCLfwd):
        self.W = W         # Weight [N]
        self.h = h     # Height [m]
        self.lfus = lfus # Length of the fuselage
        self.hsus = hfus # Height of the fuselage [m]
        self.wfus = wfus # Maximum width of the fuselage [m]
        self.Srear = Srear # Rear wing area [m^2]
        self.Sfwd = Sfwd   # Forward wing area [m^2]
        self.S = Srear+Sfwd # Aircraft wing area [m^2]
        self.cfwd = cfwd         # Average chord [m]
        self.crear = crear  # Average chord [m]
        self.bfwd = bfwd         # Wing span [m]
        self.brear = brear # Wing span [m]
        self.taper = taper # Wing taper ratio [-]
        self.CLfwd,self.CLrear  = CLfwd,CLrear # DESIGN FOR CRUISE Lift coefficients [-]
        self.Afwd, self.Arear = Afwd, Arear # Aspect ratio of both wings [-]
        self.Sweepc4fwd = Lambda_c4_fwd # Sweep at c/2 [rad]
        self.Sweepc4rear = Lambda_c4_rear # Sweep at c/2 [rad]
        self.Sweepc2fwd = self.Sweep(Afwd,self.Sweepc4fwd,50,25)
        self.Sweepc2rear = self.Sweep(Arear, self.Sweepc4rear, 50, 25)
        self.th0 = theta0  # Initial pitch angle [rad]
        self.V0 = V0       # Initial speed [m/s]
        # self.M0 = M0       # Initial mach number [-]
        # self.Re = self.rho*self.V0*self.lfus/self.mu
        self.CLafwd, self.CLarear = CLafwd, CLarear # Wing lift curve slopes for both wings [1/rad]
        self.Cmacfwd, self.Cmacrear = Cmacfwd,Cmacrear
        self.CD0 = CD0 # C_D_0 of forward wing
        self.xacfwd = 0.25*self.cfwd
        self.xacrear = self.lfus - (1 - 0.25) * self.crear
        # self.de_da = self.deps_da(self.Sweepc4fwd,self.bfwd,self.lh(),self.hfus,self.Afwd,self.CLafwd)
        self.taper_v = 0.4
        self.Vs = Vstall # Stall speed [m/s]
        self.Vmc = 1.2*self.Vs # Minimum controllable speed [m/s]
        self.xcg = xcg
        self.c = self.Sfwd/self.S*self.cfwd+self.Srear/self.S*self.crear
        self.dCLfwd = dCLfwd

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
    def tau_e(self,Se_S):
        """
        Inputs:
        :param Se_S: Elevator surface to wing ratio [-]
        :return: Elevator Effectiveness [-]
        """
        x = Se_S
        tau_a = -6.624*x**4+12.07*x**3-8.292*x**2+3.295*x+0.004942
        return tau_a
    def dCLfwd_f(self,Se_S,be_b,de_max):
        dCL = self.tau_e(Se_S) * self.CLafwd * be_b * de_max * np.pi / 180/100
        return dCL
    def plotting(self,Se_S,be_b,de_max):
        """
        Inputs:
        :param Se_S: Elevator surface to wing ratio [-]
        :param de_max: Maximum elevator deflection
        :return: Plots
        """
        mindCL = self.dCLfwd
        if isinstance(be_b,float):
            mindCL = np.ones(len(be_b))*mindCL
            dCL_array = self.tau_e(Se_S)*self.CLafwd*be_b*de_max*np.pi/180/100
            plt.plot(be_b,mindCL,label=r"Minimum value required $\Delta C_{L_{fwd}}$")
            plt.plot(be_b,dCL_array,label=r"$\Delta C_{L_{fwd}}$")
            plt.xlabel(r"$b_e/b_{fwd} [m]$",fontsize=14)
            plt.ylabel(r"$\Delta C_{L_{fwd}}$",fontsize=14)
            # plt.vlines(b1, min(Clda_array),max(Clda_array),"r",label=r"Smallest limit set by $b_1$")
            plt.ylim(min(dCL_array))
            plt.xlim(min(be_b))
            plt.legend()
            plt.show()
        else:
            X, Y = np.meshgrid(be_b, Se_S)
            Z =  self.dCLfwd_f(Y,X,de_max)
            fig, ax = plt.subplots(1, 1)
            # ax.add_artist(ab)
            # levels = [0,0.1,1,1.]
            cp = ax.contourf(X, Y, Z, cmap='coolwarm')
            minimum = ax.contour(X, Y, Z, [mindCL], colors=["k"])
            plt.clabel(minimum)
            cbar = plt.colorbar(cp, orientation="horizontal")
            cbar.set_label(r"$\Delta C_{L_{fwd}} [-]$")
            plt.ylabel(r"$S_e/S_{fwd}$ [-]", fontsize=12)
            plt.xlabel(r"$b_e$ [$\% b_{fwd}$]", fontsize=12)
            # plt.vlines(b1,min(Sa_S),max(Sa_S),"r",label=r"Smallest limit set by $b_1$")
            plt.show()




