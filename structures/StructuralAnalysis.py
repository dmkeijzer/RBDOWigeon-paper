from Geometry import HatStringer, JStringer, ZStringer, WingBox, WingStructure, StructuralError
from SolveLoads import WingLoads, Engines, Fatigue
from Weight import *
from Material import Material
from Draw import InternalLoading, DrawFatigue
from Equilibrium import RunningLoad
import warnings
import numpy as np
warnings.filterwarnings('ignore')

Cl = [float(c.strip('\n')) for c in """0. 0.07012725 0.1396002  0.20779006 0.27412298 0.33811438
 0.39940413 0.45778292 0.51319906 0.56574244 0.61561101 0.66307066
 0.7084175  0.75194759 0.79393547 0.83462059 0.87420005 0.91282594
 0.9506056  0.98760375 1.02384567 1.05932065 1.09398561 1.12776843
 1.16057106 1.19227226 1.22273008 1.25178397 1.27925667 1.30495596
 1.3286762  1.35019983""".strip("\n").split(' ') if c][::-1]

Cd = [float(c.strip('\n')) for c in """0 0.01634525 0.02443397 0.03061296 0.03503482 0.03792653
 0.03956237 0.04023399 0.0402226  0.03977798 0.03910679 0.03836955
 0.03768385 0.03713102 0.03676384 0.03661383 0.03669755 0.03702143
 0.03758554 0.03838613 0.03941739 0.04067269 0.04214514 0.04382809
 0.04571515 0.0478003  0.0500777  0.05254152 0.05518571 0.0580037
 0.06098806 0.06413016""".strip("\n").split(' ') if c][::-1]

inputs = dict(MAC = 1.265147796494402, # Mean Aerodynamic Chord [m]
cruise = True, # boolean depending on whether cruise or take-off is being considered
w_back = True, # will analyse the back wing if True
taper = 0.45, # [-]
rootchord = 1.6651718350228892, # [m]
thicknessChordRatio = 0.17, # [-]
xAC = 0.25, # [-] position of ac with respect to the chord
mtom = 3024.8012022968796, # maximum take-off mass from statistical data - Class I estimation
S1 = 9.910670535618632, 
S2 = 9.910670535618632, # surface areas of wing one and two
span1 = 8.209297146662843,
span2 = 8.209297146662843,
nmax = 3.43, # maximum load factor
Pmax = 17, # this is defined as maximum perimeter in Roskam, so i took top down view of the fuselage perimeter
lf = 7.348878876267166, # length of fuselage
wf = 1.38, # width of fuselage
m_pax = 88, # average mass of a passenger according to Google
n_prop = 12, # number of engines
n_pax = 5, # number of passengers (pilot included)
pos_fus = 2.9395515505068666, # fuselage centre of mass away from the nose
pos_lgear = 3.875, # landing gear position away from the nose
pos_frontwing = 0.5,
pos_backwing = 6.1, # positions of the wings away from the nose
m_prop = [502.6006543358783/12]*12, # list of mass of engines (so 30 kg per engine with nacelle and propeller)
pos_prop =  [-0.01628695, -0.01628695, -0.01628695, -0.01628695, -0.01628695, -0.01628695, 
             5.58371305,  5.58371305,  5.58371305,  5.58371305,  5.58371305,  5.58371305], # 8 on front wing and 8 on back wing
Mac = 0.002866846692576361, # aerodynamic moment around AC
flighttime = 1.5504351809662442, # [hr]
turnovertime = 2, # we dont actually need this xd
takeofftime = 262.839999999906/3600,
engineMass = 502.6006543358783 * 9.81 / 8,
Thover = 34311.7687171136/12,
Tcruise = 153.63377687614096,
p_pax = [1.75, 3.75, 3.75, 6, 6],
battery_pos = 0.5,
cargo_m = 35, cargo_pos = 6.5, battery_m = 886.1868116321529,
materialdata = '../data/materials.csv',
CL = Cl, CD = Cd, # Aerodynamics
Vcruise = 72.18676185339652, # Cruise speed [m/s]
)

class Structure:
    def __init__(self, **inputs):
        self.__dict__.update(inputs)
        base, height = 0.75 - 0.15, 0.11571117509557907 + 0.03145738125495376 # x/c, y/c
        self.pos = np.linspace(0, self.span1/2, len(self.CL))
        lift_area = RunningLoad([np.array(self.CL), [0]*len(self.CL)], positions = self.pos, axis = 2).force()[0]
        drag_area = RunningLoad([np.array(self.CD), [0]*len(self.CD)], positions = self.pos, axis = 2).force()[0]
        self.n_ult = self.nmax*1.5
        self.liftd = np.array(self.CL) / lift_area * self.n_ult * self.mtom / 4 * 9.80665
        self.dragd = np.array(self.CD) / drag_area * (self.Tcruise * 12) / 4
        self.span = self.span2 if self.w_back else self.span1
        self.hatGeom = dict(bflange1 = self.rootchord / (self.ntofit * 3), 
                            bflange2 = self.rootchord / (self.ntofit * 3),
                            tflange = self.rootchord / (self.ntofit * 3),
                            vflange = 1.5 * self.rootchord / (self.ntofit * 3),
                            tstr = self.thicknessOfStringer)
        self.normalBox = WingBox(self.thicknessOfSkin, self.thicknessOfSpar, base, height)
        self.normalBox.StrPlacement(self.nStrT, self.nStrB, stringerGeometry = self.hatGeom, stringerType = 'Hat')
        print(self.normalBox.str[0])
        self.wing = WingStructure(self.span, self.taper, self.rootchord, self.normalBox)
        self.enginePlacement = list(np.linspace(0.3 + self.wf / 2, self.span1/2, int(len(self.pos_prop)/4)))
        self.AR1 = self.span1 **2 / self.S1
        self.AR2 = self.span2 **2 / self.S2
        self.omax, self.taumax, self.Ymax, self.cycles, self.matsk, self.matstr, self.loads, self.critbuckling = [None]*8
        self.omin, self.taumin, self.Ymin = [None]*3
        self.wingWeight = None
        self.tfat, self.fatcyc = [None]*2
        self.fatigue = None
        self.matstr = Material.load(**(self.stringerMat | {'file': self.materialdata}))
        self.matsk = Material.load(**(self.skinMat | {'file': self.materialdata}))

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    __getitem__ = lambda self, key: self.__dict__[key]
        
    def compute_stresses(self, nStrT, nStrB, thicknessOfSkin, thicknessOfSpar, **kwargs):
        args = dict(span=self.span, taper=self.taper, cr=self.rootchord, tsk=thicknessOfSkin,
                    tsp=thicknessOfSpar, toc=self.thicknessChordRatio, nStrT=nStrT, nStrB=nStrB,
                    strType='Hat', strGeo=self.hatGeom, mac=self.MAC, xac=self.xAC,
                    engines=Engines(self.Thover, self.Tcruise, self.enginePlacement,self.engineMass), frac=0.6)

        self.loads = WingLoads(**args)
        wing = Wing(self.mtom, self.S1, self.S2, self.n_ult, self.AR1, self.AR2, [self.pos_frontwing, self.pos_backwing])
#         print(wing.mass)
        self.wingWeight = wingWeight = wing.mass[0]
        fuselage = Fuselage(self.mtom, self.Pmax, self.lf, self.n_pax, self.pos_fus)
        lgear = LandingGear(self.mtom, self.pos_lgear)
        props = Propulsion(self.n_prop, self.m_prop, self.pos_prop)

        w = Weight(self.m_pax, wing, fuselage, lgear, props,
                   cargo_m = self.cargo_m, cargo_pos = self.cargo_pos, battery_m = self.battery_m,
                   battery_pos = self.battery_pos, p_pax = self.p_pax)
        
        
        lift, wgt = self.loads.internalLoads([self.pos, self.dragd], [self.pos, self.liftd],
                                        [self.pos, [self.Mac / self.span]*len(self.pos)], wingWeight)
        
        
        if self.cruise:
            reactionsCruise = self.loads.equilibriumCruise([self.pos, self.dragd], [self.pos, self.liftd],
                                                  [self.pos, [self.Mac / self.span]*len(self.pos)], self.wingWeight)
            coords, o_cr, tau_cr, Ymcr = self.loads.stressesCruise()
            (self.omin, self.omax), (self.taumin, self.taumax) = WingLoads.extreme(coords, o_cr), WingLoads.extreme(coords, tau_cr)
            self.Ymin, self.Ymax = WingLoads.extreme(coords, Ymcr)
        else:
            reactionsVTO = self.loads.equilibriumVTO(wingWeight)
            VxVTO, MyVTO = self.loads.internalLoadsVTO(wingWeight)
            coords, o_VTO, tau_VTO, YmVTO = self.loads.stressesVTO()
            self.Ymin, self.Ymax = WingLoads.extreme(coords, YmVTO)
            (self.omin, self.omax), (self.taumin, self.taumax) = WingLoads.extreme(coords, o_VTO), WingLoads.extreme(coords, tau_VTO)

        return [[self.omin, self.omax], [self.taumin, self.taumax], [self.Ymin, self.Ymax]]

    def compute_fatigue(self, matsk):
        wingWeight = self.wingWeight
        liftdist = np.array(self.liftd) * self.n_ult
        dragdist = np.array(self.dragd) * self.n_ult
        pos, liftd, dragd, Mac, span, wingWeight = [self[k] for k in 'pos, liftd, dragd, Mac, span, wingWeight'.split(', ')]
        
        fatigue_reactionsCruise = self.loads.equilibriumCruise([pos, dragd], [pos, liftd], [pos, [Mac / span]*len(pos)], wingWeight)
        fatigue_lift, fatigue_wgt = self.loads.internalLoads([pos, dragd], [pos, liftd], [pos, [Mac / span]*len(pos)], wingWeight)
        coords, ocrf, taucrf, Ymcrf = self.loads.stressesCruise()

        fatigue_reactionsVTO = self.loads.equilibriumVTO(wingWeight)
        fatigue_VxVTO, fatigue_MyVTO = self.loads.internalLoadsVTO(wingWeight)
        coords, oVTOf, tauVTOf, YmVTOf = self.loads.stressesVTO()

        fatigue_reactionsVTOgr = self.loads.equilibriumVTO(wingWeight, ground = True)
        fatigue_VxVTOgr, fatigue_MyVTOgr = self.loads.internalLoadsVTO(wingWeight, ground = True)
        coords, oVTOfgr, tauVTOfgr, YmVTOfgr = self.loads.stressesVTO()

        _, (coor, maxDif) = self.loads.extreme(coords, oVTOf - ocrf)
 
        ind = [i for i in range(len(coords)) if np.all(coords[i] == coor)][0]

        oVTOfgrmd, oVTOfmd, ocrfmd = oVTOfgr[ind]*1e-6, oVTOf[ind]*1e-6, ocrf[ind]*1e-6

        fatigue = Fatigue(oVTOfgrmd, oVTOfmd, ocrfmd,
                          self.flighttime, self.turnovertime, self.takeofftime, matsk)

        self.tfat, self.fatcyc = fatigue.determineCycle()
        fdf = fatigue.getCycles()
        self.cycles = fatigue.MinersRule()
        err = abs((self.cycles - matsk.BasquinLaw(abs(oVTOfgrmd - ocrfmd))) / self.cycles)
        self.fatigue = fatigue
        if self.cycles > matsk.BasquinLaw(abs(oVTOfgrmd - ocrfmd)):
            raise StructuralError(f"Invalid Number of Fatigue Cycles: {self.cycles}")
        return self.cycles
    
    def compute_buckling(self, stringerMat, skinMat):

        root = self.loads.wing(0)
        EofStringers = self.matstr.E
        vOfStringers = self.matsk.v
        yieldOfStringers = self.matstr.oy
        EofSkin = self.matsk.E
        vOfSkin = self.matsk.v
        self.critbuckling = root.Bstress(EofStringers, vOfStringers, yieldOfStringers, EofSkin, vOfSkin)
        return self.critbuckling

    def optimize(self):
        
        nStrT, nStrB, thicknessOfSkin, thicknessOfSpar = \
        [self[k] for k in 'nStrT, nStrB, thicknessOfSkin, thicknessOfSpar'.split(', ')]

        while True:
            (omin, omax), (taumin, taumax), (Ymin, Ymax) = \
            self.compute_stresses(nStrT, nStrB, thicknessOfSkin, thicknessOfSpar) 
            root = self.loads.wing(0)
#             print(f"Mass of wing: {self.loads.mass(self.matsk)} kg")
            print(f"{nStrT, nStrB, 1e3*thicknessOfSkin, 1e3*thicknessOfSpar = }")
            if omin[1] > 0:
                raise StructuralError("Positive Compression Stress Encountered: " + str(omin[1]))
            if Ymax[1] < omax[1]:
                raise StructuralError("Von Mises stress less than normal stress")
            if Ymax[1] < taumax[1]:
                raise StructuralError("Von Mises stress less than shear stress")
            critbuckling = self.compute_buckling(self.matstr, self.matsk)
            cycles = self.compute_fatigue(self.matsk)
            print(f'Fatigue life: {cycles} cycles')
            yieldMargin, bucklingmargin = self.matsk.oy / Ymax[1], abs(critbuckling / omin[1])
            print(f"{critbuckling*1e-6, self.matsk.oy*1e-6 = }")
            print(f"Minimal stresses {omin[1]*1e-6, Ymax[1]*1e-6, taumin[1]*1e-6 = }")
            print(f"Positions {list(omin[0]), list(Ymax[0]), list(taumin[0]) = }")
            print(f"Maximal stresses {omax[1]*1e-6, Ymax[1]*1e-6, taumax[1]*1e-6 = }")
            print(f"Positions {list(omax[0]), list(Ymax[0]), list(taumax[0]) = }")
            if omin[1] <= -critbuckling or Ymax[1] >= self.matsk.oy:
                print("Fail\n")
                if bucklingmargin > yieldMargin:
                    if abs(Ymax[0][0] - root.b/2) <= 1.5*root.tsp or abs(Ymax[0][0] + root.b/2) <= 1.5*root.tsp:
                        thicknessOfSpar += 0.0001
                    elif abs(Ymax[0][1] - root.h/2) <= root.tsk or abs(Ymax[0][1] + root.h/2) <= root.tsk:
                        thicknessOfSkin += 0.0001
                else:
                    nStrT += 1

            elif 1 < bucklingmargin < 1.2 and 1 < yieldMargin < 1.2:
                if self.cycles < 15*365*4:
                    raise StructuralError(f"Fatigue Life too low: {self.cycles}")
                else:
                    damage = self.fatigue.CrackGrowth(1.2 * 0.375 / 1000, root.tsk, round(self.cycles))
                    print(f"Fatigue Life: {self.cycles} cycles, tolerance: {damage} cycles")
                    break
            else:
                print("Success\n")
                if bucklingmargin > yieldMargin:
                    nStrT -= 1
                else:
                    if abs(Ymax[0][0] - root.b/2) <= 1.5*root.tsp or abs(Ymax[0][0] + root.b/2) <= 1.5*root.tsp:
                        thicknessOfSkin -= 0.0001
                    elif abs(Ymax[0][1] - root.h/2) <= root.tsk or abs(Ymax[0][1] + root.h/2) <= root.tsk:
                        thicknessOfSpar -= 0.0001
        
        self.nStrT, self.nStrB, self.thicknessOfSkin, self.thicknessOfSpar = nStrT, nStrB, thicknessOfSkin, thicknessOfSpar
        return nStrT, nStrB, thicknessOfSkin, thicknessOfSpar

    plotNVMcruise = lambda self: InternalLoading(0, self.span/2, Vx = self.loads.Vx, Vy = self.loads.Vy,
                                                Mx = self.loads.Mx, My = self.loads.My, T = self.loads.T)

    plotNVMVTOL = lambda self: InternalLoading(0, self.span/2, Vx = self.loads.ViVx, My = self.loads.ViMy)
    
    plotFatigue = lambda self: DrawFatigue(self.tfat, self.fatcyc)

state = dict(nStrT=2, nStrB=1,
             thicknessOfSkin=1.3e-3, thicknessOfSpar=18e-3,
             thicknessOfStringer=1e-3, ntofit=20, stringerMat = dict(material='Al 7075', Condition='T6'),
                skinMat = dict(material='Al 7075', Condition='T6'))

aluminum = Material.load(file='../data/materials.csv')
struct = Structure(**(inputs | state ))
struct.optimize()

fig = struct.plotNVMcruise()
fig.show(renderer='iframe')
fig.write_html('NVM_cruise.html')

fig2 = struct.plotNVMVTOL()
fig2.write_html('NVM_vtol.html')

struct.plotFatigue().write_html('fatigue.html')