import sys
import json
import numpy as np
sys.path.append('../')
sys.path.append('../Sizing')
from constants import *
from maneuvre import plotgustenv, plotmaneuvrenv

from cg_est import Wing, Fuselage, LandingGear, Propulsion, Weight
from SolveLoads import SolveACLoads, SolveWingLoads, SolveVLoads
from Analysis import WingBox, WingStructure
from Material import Material

config = inputconfig
WoS = 1422
Pmax = 8.77182
mProp = 400 / N_cruise
thickness = 3e-3
w_fus= 1.3; h_fus=1.6; l_fus=4

nmax = max(plotgustenv(0.75 * V_cruise, V_cruise, CLalpha_back, WoS), plotmaneuvrenv(WoS, V_cruise, CLmax_back))

w = Weight(95, Wing(mTO, S_front, S_back, 1.5*nmax, AR, [0.4, 3.6], config),
           Fuselage(mTO, Pmax, l_fus, 5, l_fus/2, config),
          LandingGear(mTO, l_fus/2),
          Propulsion(N_cruise, [mProp]*N_cruise, pos_prop=[3.6]*int(N_cruise/2) + [0.4]*int(N_cruise/2)),
          cargo_m, cargo_p, Bat_mass, l_fus/2, [0.8, 1.3, 1.3, 2.5, 2.5])

wf = w.print_weight_fractions()
b = (S_front * AR) ** 0.5

LpWing = SolveACLoads(w.mtom_cg, *w.wing.pos)



wingEquation = SolveWingLoads(MAC1, b, 1.5*nmax*LpWing[0]/2, mTO / LD_ratio, w.wing.get_weight()[0]/2, 
                              mTO / (LD_ratio*N_cruise), N_cruise)
wingEquation.SetupEquation()
Fx, Fy, Fz, Mx, My, Mz = wingEquation.SolveEquation()
wingS = WingStructure(wingEquation)
N, Vx, Vy, Mx, My, Mz = wingS.compute_loading()

box = WingBox(thickness, 0.8 * c_r, 0.8 * 0.17 * c_r)
tau = lambda x, y, z: box.tau(x, y, Vx(z), Vy(z), My(z))
ozz = lambda x, y, z: box.o(x, y, Mx(z), My(z))

stresses = np.array([[ozz(x, y, 0) for x in np.linspace(-box.b/2, box.b/2)] for y in np.linspace(-box.h/2, box.h/2)], dtype='float64')
am = stresses.argmax()

omax, taumax = stresses.flatten()[am]*1e-6, tau(box.b/2, -box.h/2, 0)*1e-6

Ymax = (omax ** 2 + 3 * taumax ** 2) ** 0.5

aluminum = Material.load(file='materials.csv', material='Al 6061', Condition='T6')
N = aluminum.ParisFatigueN(stresses.flatten()[am], box.b, 2*1e-3, box.t/2)
# aluminum.StressConcentration(aluminum.beta(0.01), 50e-3, 100*1e6)

xd, yd = wingS.compute_deflections(aluminum.E, box.Ixx(), box.Iyy())

critBuckling = aluminum.buckling(box.h, box.t)*1e-6

output = dict(config = config, WingLoading = WoS, maxPerimeter = Pmax, mPropellers = mProp, weightFractions = wf,
              MaxNormalStress=omax, MaxShearStress=taumax, critBucklingStress=critBuckling, fatigueLife=N, deflectionX = xd(b/2),
             deflectionY = yd(b/2), maxVonMises = Ymax, EOW = w.oem*9.81, MTOW = w.mtom*9.81, cgOEM = w.oem_cg, cgMTOM = w.mtom_cg,
             Passed = bool(omax < critBuckling and N > 365 * 3 * 15 and Ymax < aluminum.oyield), w_fus= 1.3, h_fus=1.6, l_fus=4)




with open("output.json", "r") as o:
    dic = json.loads(o.read())

dic[["Tandem", "Box", "Single"][config - 1]] = output
print(output)

op = json.dumps(dic, indent=3)

with open("output.json", "w") as out:
    out.write(op)


# with open(f"../data/inputs_config_{config}.json", "r") as f:
#     dic = json.loads(f.read())

# dic["Structures"] = output
# op = json.dumps(dic, indent=3)

# with open(f"../data/inputs_config_{config}.json", "w") as f:
#     f.write(op)