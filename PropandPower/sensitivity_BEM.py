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

B = 5
rpm = 2500

Vs = np.arange(45, 80)
rs = np.arange(0.35, 0.7, 0.01)
X, Y = np.meshgrid(rs, Vs[::-1])  # Reorder Vs, idk why it is necessary

Z = np.ones(np.shape(X))

for y in range(len(Vs)):
    for x in range(len(rs)):

        # Check combinations of number of blades and rpm
        V_cruise = Vs[::-1][y]  # Reorder Bs here too
        R = rs[x]

        # Load the propeller
        propeller = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V_cruise, N_stations, a, RN_spacing, T=T_cr_per_eng)

        zeta, design, V_e, coefs = propeller.optimise_blade(0)

        # The parameter of interest is the propeller efficiency
        Z[y][x] = design[5]

# Plot sensitivity plot
cont = plt.contourf(X, Y, Z, cmap='coolwarm', levels=20)
cbar = plt.colorbar(cont, orientation="vertical")

cbar.set_label(r'$\eta$')
plt.ylabel("V [m/s]", fontsize=12)
plt.xlabel("R [m]", fontsize=12)

plt.show()

