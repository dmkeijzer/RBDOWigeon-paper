import numpy as np
from scipy.linalg import null_space
from matplotlib import pyplot as plt
from matplotlib import colors as mc

class Stab_Derivatives:
    def __init__(self,W,h,cfwd,crear,bfwd,brear,V0,T0,M0,CD0,CL0,theta0,CLafwd,CLarear,Sfwd,Srear,Gamma, Lambda_c4,bv,Sv):
        self.W = W         # Weight [N]
        self.h = h     # Height [m]
        self.Srear = Srear # Rear wing area [m^2]
        self.Sfwd = Sfwd   # Forward wing area [m^2]
        self.S = Srear+Sfwd # Aircraft wing area [m^2]
        self.cfwd = cfwd         # Average chord [m]
        self.crear = crear  # Average chord [m]
        self.bfwd = bfwd         # Wing span [m]
        self.brear = brear # Wing span [m]
        self.Sweepc4 = Lambda_c4 # Sweep at c/4 [rad]
        self.bv = bv       # Vertical tail span [m]
        self.Sv = Sv       # Vertical tail area [m^2]
        self.th0 = theta0  # Initial pitch angle [rad]
        self.V0 = V0       # Initial speed [m/s]
        self.M0 = M0       # Initial mach number [-]
        self.CL0 = CL0     # Initial lift coefficient [-]
        self.CD0 = CD0     # Initial drag coefficient (not CD_0)[-]
        self.T0 = T0       # Initial thrust [N]
        self.Gamma_fwd = Gamma # Forward wing dihedral [rad]
        self.CLafwd, self.CLarear = CLafwd, CLarear # Wing lift curve slopes for both wings [1/rad]
