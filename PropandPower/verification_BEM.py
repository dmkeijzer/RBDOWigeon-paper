import matplotlib.pyplot as plt
import numpy as np
import BEM as BEM
import PropandPower.prelim_ADT as ADT
import constants as const
import Aero_tools as at

g0 = const.g
rho0 = const.rho_0

ISA = at.ISA(1000)

rho = ISA.density()
dyn_visc = ISA.viscosity_dyn()
a = ISA.soundspeed()


"""
Check the exit speed of BEM with ADT, they should be similar
"""

MTOM = 3000

n_prop = 12
# B = 20
rpm = 2500
R = 0.55
xi_0 = 0.1

A_prop = np.pi * R**2 - (np.pi * (R*xi_0)**2)
A_tot = A_prop * n_prop

DiskLoad = MTOM / A_tot

V_cr = 74
T_cr_per_eng = 200

ActDisk = ADT.ActDisk_verif(V_cr, T_cr_per_eng*n_prop, rho, A_tot)

# print("Cruise exit speed (ADT):", ActDisk.v_e_cr())
#
# Bs = []
# Ves = []
# for B in range(3, 26):
#     blade = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V_cr, 100, a, 100000, T=T_cr_per_eng)
#
#     blade_design = blade.optimise_blade(0)
#
#     # Check exit speed
#     Ves.append(blade_design[0]*V_cr + V_cr)
#     Bs.append(B)
#
# # print("Cruise exit speed (BEM)", blade_design[0]*V_cr + V_cr)
# #
# # print("Ratio:", ActDisk.v_e_cr()/(blade_design[0]*V_cr + V_cr))
# # print("")
#
# # Plot the propeller exit speed against the number of blades
# plt.ylim(70, 90)
# plt.plot(Bs, Ves, label='Blade Element Momentum Theory')
# plt.hlines(ActDisk.v_e_cr(), Bs[0], Bs[-1], label='Actuator Disk Theory')
# plt.xlabel("B [-]")
# plt.ylabel("Slipstream speed [m/s]")
# plt.legend()
# plt.show()
#
# print("#######################################")
# print("")
#
#
# """
# Plot efficiency against J
#
# J = V/(nD)
# """
#
# # Fix n and D, change only V
# D = 2*R
# n = rpm / 60
# B = 5
#
# Js = []
# effs = []
# for V in range(80, 150):
#     blade = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V, 100, a, 100000, T=T_cr_per_eng)
#     blade_design = blade.optimise_blade(0)
#
#     # Check the advance ratio
#     J = V/(n*D)
#     Js.append(J)
#
#     # Compute the efficiency
#     eff = blade_design[1][5]
#     effs.append(eff)
#
# # Plot efficiency against advance ratio
# plt.plot(Js, effs)
# plt.xlabel("Advance ratio, J = V/(nD) [-]")
# plt.ylabel(r'$\eta$ [-]')
#
# plt.show()

"""
Plot efficiency against thrust for constant speed and rpm

"""
V = 75
B = 5
rpm = 2000
R = 0.6

Ts = []
effs = []

for T_cr_per_eng in range(100, 350, 10):
    blade = BEM.BEM(B, R, rpm, xi_0, rho, dyn_visc, V, 100, a, 100000, T=T_cr_per_eng)
    blade_design = blade.optimise_blade(0)

    # Check the thrust level
    Ts.append(T_cr_per_eng)

    # Compute the efficiency
    eff = blade_design[1][5]
    effs.append(eff)

# Plot efficiency against advance ratio
plt.plot(Ts, effs)
plt.xlabel("Thrust [N]")
plt.ylabel(r'$\eta$ [-]')

plt.show()
