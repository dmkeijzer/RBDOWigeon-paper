import numpy as np
from structures.Equilibrium import *
from constants import *

def SolveACLoads(cg: float, acf: float, acb: float) -> :
    Weight = PointLoad([0, - mTO * 9.81, 0], [cg[0] if isinstance(cg, np.ndarray) else cg, 0, 0])
    LFront = PointLoad([0, 1, 0], [acf, 0, 0])
    LBack = PointLoad([0, 1, 0], [acb, 0, 0]) if acb != 0 else Moment([0, 1, 0])
    motion = EquilibriumEquation(kloads = [Weight], ukloads=[LFront, LBack])
    motion.SetupEquation()
    return list(motion.SolveEquation())

def SolveWingLoads(MAC, b, Lwing, Dwing, mWing, TpE, nE):
    pos = np.linspace(0, b / 2)
    WingWeight = RunningLoad([[0]*len(pos), [- mWing * 9.81 / b]*len(pos)], pos, axis=2)
    Lift = RunningLoad([[0]*len(pos), [Lwing / b] * len(pos)], pos, axis=2)
    Drag = RunningLoad([[Dwing / b] * len(pos), [0]*len(pos)], pos, axis=2)
    Thrust = [PointLoad([-TpE, 0, 0], [0, 0, i]) for i in np.linspace(0, b/2, nE)]
    MomentAC = Moment(value=[0, 0, 30])

    Fixedx = PointLoad([1, 0, 0], [0.5 * MAC, 0, 0])
    Fixedy = PointLoad([0, 1, 0], [0.5 * MAC, 0, 0])
    Fixedz = PointLoad([0, 0, 1], [0.5 * MAC, 0, 0])

    FixedMomentx, FixedMomenty, FixedMomentz = Moment([1, 0, 0]), Moment([0, 1, 0]), Moment([0, 0, 1])
    wingequation = EquilibriumEquation(kloads=[WingWeight, Lift, Drag, MomentAC] + Thrust,
                                       ukloads=[Fixedx, Fixedy, Fixedz, FixedMomentx, FixedMomenty, FixedMomentz])
    wingequation.SetupEquation()
    return wingequation

def SolveVLoads(cg, acf, acb):
    Weight = PointLoad([0, - mTO * 9.81, 0], [cg[0] if isinstance(cg, np.ndarray) else cg, 0, 0])
    if inputconfig == 1:
        Trear = PointLoad([0, 1, 0], [acb, 0, 0])
        Tfwd = PointLoad([0, 1, 0], [acf, 0, 0])
    elif inputconfig == 2:
        Trear = PointLoad([0, 1, 0], [acb + MAC2*0.75, 0, 0])
        Tfwd = PointLoad([0, 1, 0], [acf + MAC1*0.75, 0, 0])
    elif inputconfig == 3:
        Tmid = PointLoad([0, Max_T_wing_engine, 0], [cg, 0, 0])
        Trear = PointLoad([0, 1, 0], [acb, 0, 0])
        Tfwd = PointLoad([0, 1, 0], [acf, 0, 0])

    motion = EquilibriumEquation(kloads=[Weight] + ([Tmid] if inputconfig == 3 else []), ukloads=[Trear, Tfwd])
    motion.SetupEquation()
    return list(motion.SolveEquation())

def SolveVWingLoads(MAC, b, Dwing, mWing, TpE, nE):
    pos = np.linspace(0, b / 2)
    WingWeight = RunningLoad([[(mWing * 9.81 + Dwing) / b]*len(pos), [0]*len(pos)], pos, axis=2)
    Thrust = [PointLoad([-TpE, 0, 0], [0, 0, i]) for i in np.linspace(0, b/2, round(nE/4))]
    Fixedx = PointLoad([1, 0, 0], [0.5 * MAC, 0, 0])
    FixedMomenty = Moment([0, 1, 0])
    wingequation = EquilibriumEquation(kloads=[WingWeight] + Thrust,
                                       ukloads=[Fixedx, FixedMomenty])
    wingequation.SetupEquation()

    return wingequation
