import sys
sys.path.append('../')

import numpy as np
from Equilibrium import *
from constants import *

def SolveACLoads(cg, acf, acb):
    Weight = PointLoad([0, - mTO * 9.81, 0], [cg, 0, 0])
    LFront = PointLoad([0, 1, 0], [acf, 0, 0])
    LBack = PointLoad([0, 1, 0], [acb, 0, 0])
    motion = EquilibriumEquation(kloads = [Weight], ukloads=[LFront, LBack])
    motion.SetupEquation()
    return list(motion.SolveEquation())

def SolveWingLoads(MAC, b, Lwing, Dwing, mWing, TpE, nE):
    pos = np.linspace(0, b / 2)
    WingWeight = RunningLoad([[0]*len(pos), [- mWing * 9.81 / b]*len(pos)], pos, axis=2)
    Lift = RunningLoad([[0]*len(pos), [Lwing * 2 / b] * len(pos)], pos, axis=2)
    Drag = RunningLoad([[Dwing * 2 / b] * len(pos), [0]*len(pos)], pos, axis=2)
    Thrust = [PointLoad([-TpE, 0, 0], [0, 0, i]) for i in np.linspace(0, b, nE)]
    MomentAC = Moment(value=[0, 0, 30])

    Fixedx = PointLoad([1, 0, 0], [0.5 * MAC, 0, 0])
    Fixedy = PointLoad([0, 1, 0], [0.5 * MAC, 0, 0])
    Fixedz = PointLoad([0, 0, 1], [0.5 * MAC, 0, 0])

    FixedMomentx, FixedMomenty, FixedMomentz = Moment([1, 0, 0]), Moment([0, 1, 0]), Moment([0, 0, 1])
    wingequation = EquilibriumEquation(kloads=[WingWeight, Lift, Drag, MomentAC] + Thrust,
                                       ukloads=[Fixedx, Fixedy, Fixedz, FixedMomentx, FixedMomenty, FixedMomentz])
    wingequation.SetupEquation()
    return list(wingequation.SolveEquation())

if __name__ == '__main__':
    print(ACLoads := SolveACLoads(1.95, 0.5, 3.5))
    print(WingLoads := SolveWingLoads(0.2, 11.2, ACLoads[0], 800, mTO / 8, 100, 3))
