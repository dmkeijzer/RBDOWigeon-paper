import numpy as np
import BEM as BEM
import Aero_tools as at
import Blade_plotter as BP
import matplotlib.pyplot as plt

# ISA = at.ISA(1000)
ISA = at.ISA(1000)
a = ISA.soundspeed()
rho = ISA.density()
dyn_visc = ISA.viscosity_dyn()


# Midterm
# B, R, rpm, xi_0, rho, dyn_vis, V_fr, N_stations, a, RN_spacing, T=None, P=None
# B = 5
xi_0 = 0.1
R = 0.55
A_prop = np.pi*R**2
MTOM = 3000

# M_t_max = 0.6
# rpm = M_t_max*a*60 / (np.pi * 2*R)
# rpm = 2000
# rpm = 1500

V_cruise = 74
V_h = 52.87
N_stations = 30
RN_spacing = 100000

T_cr_per_eng = 27.55 * 6
T_h_per_eng = MTOM*9.80665 / 12


# # Range of variables for sensitivity analysis
# Bs = np.arange(2, 9)
# rpms = np.arange(1000, 4501, 100)
# X, Y = np.meshgrid(rpms, Bs[::-1])  # Reorder Bs, idk why it is necessary
#
# Z = np.ones(np.shape(X))
#
# for y in range(len(Bs)):
#     for x in range(len(rpms)):
#
#         # Check combinations of number of blades and rpm
#         B = Bs[::-1][y]  # Reorder Bs here too
#         rpm = rpms[x]
#
#         # Load the propeller
#         propeller = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V_cruise, N_stations, a, RN_spacing, T=T_cr_per_eng)
#
#         zeta, design, V_e, coefs = propeller.optimise_blade(0)
#
#         # The parameter of interest is the propeller efficiency
#         Z[y][x] = design[5]
#
# # Plot sensitivity plot
# cont = plt.contourf(X, Y, Z, cmap='coolwarm', levels=20)
# cbar = plt.colorbar(cont, orientation="vertical")
#
# cbar.set_label(r'$\eta$')
# plt.ylabel("B", fontsize=12)
# plt.xlabel("Rotational speed [rpm]", fontsize=12)
#
# plt.show()
# Range of variables for sensitivity analysis

# B = 5
# rpm = 2500
#
# Vs = np.arange(45, 80)
# rs = np.arange(0.35, 0.7, 0.01)
# X, Y = np.meshgrid(rs, Vs[::-1])  # Reorder Vs, idk why it is necessary
#
# Z = np.ones(np.shape(X))
#
# for y in range(len(Vs)):
#     for x in range(len(rs)):
#
#         # Check combinations of number of blades and rpm
#         V_cruise = Vs[::-1][y]  # Reorder Bs here too
#         R = rs[x]
#
#         # Load the propeller
#         propeller = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V_cruise, N_stations, a, RN_spacing, T=T_cr_per_eng)
#
#         zeta, design, V_e, coefs = propeller.optimise_blade(0)
#
#         # The parameter of interest is the propeller efficiency
#         Z[y][x] = design[5]
#
# # Plot sensitivity plot
# cont = plt.contourf(X, Y, Z, cmap='coolwarm', levels=20)
# cbar = plt.colorbar(cont, orientation="vertical")
#
# cbar.set_label(r'$\eta$')
# plt.ylabel("V [m/s]", fontsize=12)
# plt.xlabel("R [m]", fontsize=12)
#
# plt.show()

B = 5
D = 2*R
rpm = 1500
R = 0.55
xi_0 = 0.1
V_cruise = 74

T_cr_per_eng = 27.55 * 12

# Base propeller
propeller = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V_cruise, N_stations, a, RN_spacing, T=T_cr_per_eng)


# Zeta init
zeta_init = 0
zeta, design, V_e, coefs = propeller.optimise_blade(zeta_init)


Omega = rpm * 2 * np.pi / 60

RN = (Omega * design[3]) * design[0] * rho / dyn_visc


rpms = np.arange(1500, 4501, 100)
deltas = np.arange(0, 15.1, 0.5)
X, Y = np.meshgrid(rpms, deltas[::-1])  # Reorder Vs, idk why it is necessary

Z = np.ones(np.shape(X))


for y in range(len(deltas)):
    for x in range(len(rpms)):

        # Check combinations of number of blades and rpm
        delta = deltas[::-1][y]  # Reorder deltas here too
        rpm = rpms[x]

        n = rpm / 60
        blade_hover = BEM.OffDesignAnalysisBEM(V_cruise, B, R, design[0], design[1] - np.deg2rad(delta), design[3],
                                               coefs[0], coefs[1], rpm, rho, dyn_visc, a, RN)

        blade_hover_analysis = blade_hover.analyse_propeller()

        # The parameter of interest is the thrust
        Z[y][x] = blade_hover_analysis[1]

# Plot sensitivity plot
cont = plt.contourf(X, Y, Z, cmap='coolwarm', levels=20)
cbar = plt.colorbar(cont, orientation="vertical")

cbar.set_label('Thrust [N]')
plt.ylabel(r'$\delta$ [deg]', fontsize=12)
plt.xlabel("Rotational speed [rpm]", fontsize=12)

plt.show()
