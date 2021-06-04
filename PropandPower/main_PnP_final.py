import numpy as np
import BEM as BEM
import Aero_tools as at
import Blade_plotter as BP

ISA = at.ISA(2500)
a = ISA.soundspeed()
rho = ISA.density()
dyn_visc = ISA.viscosity_dyn()

# B, R, rpm, xi_0, rho, dyn_vis, V_fr, N_stations, a, RN_spacing, T=None, P=None
B = 4
xi_0 = 0.05
# A_prop = 0.47*2
# R = np.sqrt(A_prop / (np.pi * (1 - xi_0**2)))
R = 0.95
A_prop = np.pi*R**2

# M_t_max = 0.6
# rpm = M_t_max*a*60 / (np.pi * 2*R)
rpm = 2700

V_cruise = 62
N_stations = 20
RN_spacing = 100000

# P_cr = 110024
# T = (P_cr*2*np.sqrt(rho*8*A_prop) * 0.65)**(2/3)

# Cessna 172, CdS = 5.93 sq ft
D = 0.551*rho*V_cruise**2/2
T = D

propeller = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V_cruise, N_stations, a, RN_spacing, T=T)

# Zeta init
zeta_init = 0
design = propeller.optimise_blade(zeta_init)[1]
# [cs, betas, alpha, E, eff, Tc, self.Pc]
print("Chord per station:", design[0])
print("")
print("Pitch per station in [deg]:", design[1]*180/(2*np.pi))
print("")
print("AoA per station in [deg]:", design[2]*180/(2*np.pi))
print("")
print("Radial coordinates [m]:", design[3])
print("")
print("D/L ratio per station:", design[4])
print("")
print("Propeller efficiency:", design[5])
print("")
print("Thrust coefficient:", design[6])
print("")
print("Power coefficient:", design[7])

# Load blade plotter
plotter = BP.PlotBlade(design[0], design[1], design[3], R, xi_0)

# Plot blade
plotter.plot_blade()
plotter.plot_3D_blade()