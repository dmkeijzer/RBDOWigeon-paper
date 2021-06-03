import numpy as np
from matplotlib import pyplot as plt
from matplotlib import colors as mc

class Control_surface:
    def __init__(self,V0,Vstall,CLfwd,CLrear,
                 CLafwd,CLarear, Clafwd,Clarear,Cd0fwd,Cd0rear,
                 Sfwd,Srear,Afwd,Arear,cfwd,crear,bfwd,brear,taper):
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
        self.V0 = V0       # Initial speed [m/s]
        self.CLafwd, self.CLarear = CLafwd, CLarear # Wing lift curve slopes for both wings [1/rad]
        # self.xacfwd = 0.25*self.cfwd
        # self.xacrear = self.lfus - (1 - 0.25) * self.crear
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

    def Clda(self,Sa_S,b1,b2):
        """
        Input:
        :param b2: Outer distance of the aileron [m]
        :return: Control derivative C_l_da [1/rad]
        """
        b_1 = b1*self.bfwd / 2 / 100
        b_2 = b2*self.bfwd / 2 / 100
        c_r = self.cfwd*3/2*(1+self.taper)/(1+self.taper+self.taper**2)
        Clda = self.CLafwd*self.tau_a(Sa_S)*c_r/(self.Sfwd*self.bfwd)*\
               (0.5*(b_2**2-b_1**2) + 2*(self.taper-1)/(3*self.bfwd)*(b_2**3-b_1**3))
        return Clda

    def Clp(self):
        c_r_fwd = self.cfwd * 3 / 2 * (1 + self.taper) / (1 + self.taper + self.taper ** 2)
        c_r_rear =  self.crear*3/2*(1+self.taper)/(1+self.taper+self.taper**2)
        Clp_fwd =-(self.Clafwd+self.Cd0fwd)*c_r_fwd*self.bfwd/(24*self.Sfwd)
        Clp_rear = -(self.Clarear + self.Cd0rear) * c_r_rear * self.brear/(24 * self.Srear)
        Clp = Clp_fwd+Clp_rear
        return Clp

    def plotting(self,Sa_S,b1,b2):
        if isinstance(Sa_S,float):
            da_max = 30*np.pi/180
            dphi_dt = 60*np.pi/180/1.3
            minClda = -(dphi_dt)*self.Clp()*max(self.bfwd,self.brear)/(2*self.Vmc*da_max)
            minClda = np.ones(len(b2))*minClda
            Clda_array = self.Clda(Sa_S,b1,b2)
            plt.plot(b2,minClda,label=r"Minimum value required $C_{l_{\delta_a}}$")
            plt.plot(b2,Clda_array,label=r"$C_{l_{\delta_a}}(b_2)$")
            plt.xlabel(r"$b_2 [m]$",fontsize=14)
            plt.ylabel(r"$C_{l_{\delta_a}} [1/rad]$",fontsize=14)
            # plt.vlines(b1, min(Clda_array),max(Clda_array),"r",label=r"Smallest limit set by $b_1$")
            plt.ylim(min(Clda_array))
            plt.xlim(min(b2))
            plt.legend()
            plt.show()
        else:
            da_max = 30 * np.pi / 180
            dphi_dt = 60 * np.pi / 180 /1.3
            minClda = -(dphi_dt) * self.Clp() * max(self.bfwd, self.brear) / (2 * self.Vmc * da_max)
            X, Y = np.meshgrid(b2, Sa_S)
            Z =  self.Clda(Y,b1, X)
            fig, ax = plt.subplots(1, 1)
            # ax.add_artist(ab)
            # levels = [0,0.1,1,1.]
            cp = ax.contourf(X, Y, Z, cmap='coolwarm')
            minimum = ax.contour(X, Y, Z, [minClda], colors=["k"])
            plt.clabel(minimum,fmt="Roll requirement")
            cbar = plt.colorbar(cp, orientation="horizontal")
            cbar.set_label(r"$C_{l_{\delta_a}} [1/rad]$")
            plt.ylabel(r"$S_a/S_{fwd}$ [-]", fontsize=12)
            plt.xlabel(r"$b_2$ [$\% b_{fwd}/2$]", fontsize=12)
            # plt.vlines(b1,min(Sa_S),max(Sa_S),"r",label=r"Smallest limit set by $b_1$")
            plt.show()




