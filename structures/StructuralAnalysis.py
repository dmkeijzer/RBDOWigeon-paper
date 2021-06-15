from Geometry import HatStringer, JStringer, ZStringer, WingBox, WingStructure, StructuralError
from SolveLoads import WingLoads, Engines, Fatigue
from Weight import *
from Material import Material
from Draw import InternalLoading, DrawFatigue
import warnings
warnings.filterwarnings('ignore')


class Structure:
    def __init__(self, **inputs):
        self.__dict__.update(inputs)
        base, height = 0.75 - 0.15, 0.11571117509557907 + 0.03145738125495376 # x/c, y/c
        self.n_ult = self.nmax*1.5
        self.hatGeom = dict(bflange1 = self.rootchord / (self.ntofit * 3), 
                            bflange2 = self.rootchord / (self.ntofit * 3),
                            tflange = self.rootchord / (self.ntofit * 3),
                            vflange = 6 * self.rootchord / (self.ntofit * 3),
                            tstr = self.thicknessOfStringer)
        self.normalBox = WingBox(self.thicknessOfSkin, self.thicknessOfSpar, base, height)
        self.normalBox.StrPlacement(self.nStrT, self.nStrB, stringerGeometry = self.hatGeom, stringerType = 'Hat')
        self.wing = WingStructure(self.span, self.taper, self.rootchord, self.normalBox)
        self.AR = self.span / self.wing.chord(self.span/2)
        self.S1 = self.wing.area()
        self.omax, self.taumax, self.Ymax, self.cycles, self.matsk, self.matstr, self.loads, self.critbuckling = [None]*8
        self.omin, self.taumin, self.Ymin = [None]*3
        self.wingWeight = None
        self.dragd, self.liftd, self.pos = np.array(self.dragd), np.array(self.liftd), np.array(self.pos)
        self.tfat, self.fatcyc = [None]*2
        self.matstr = Material.load(**(self.stringerMat | {'file': self.materialdata}))
        self.matsk = Material.load(**(self.skinMat | {'file': self.materialdata}))

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    __getitem__ = lambda self, key: self.__dict__[key]
        
    def compute_stresses(self, nStrT, nStrB, thicknessOfSkin, thicknessOfSpar, **kwargs):
        self.dragd, self.liftd = np.array(self.dragd), np.array(self.liftd)
        args = dict(span=self.span, taper=self.taper, cr=self.rootchord, tsk=thicknessOfSkin,
                    tsp=thicknessOfSpar, toc=self.thicknessChordRatio, nStrT=nStrT, nStrB=nStrB,
                    strType='Hat', strGeo=self.hatGeom, mac=self.MAC, xac=self.xAC,
                    engines=Engines(self.Thover, self.Tcruise, self.enginePlacement,self.engineMass), frac=0.6)

        self.loads = WingLoads(**args)
        wing = Wing(self.mtom, self.S1, self.S2, self.n_ult, self.AR, [self.pos_frontwing, self.pos_backwing])
        self.wingWeight = wingWeight = wing.mass[0]
        fuselage = Fuselage(self.mtom, self.Pmax, self.lf, self.n_pax, self.pos_fus)
        lgear = LandingGear(self.mtom, self.pos_lgear)
        props = Propulsion(self.n_prop, self.m_prop, self.pos_prop)

        w = Weight(self.m_pax, wing, fuselage, lgear, props,
                   cargo_m = self.cargo_m, cargo_pos = self.cargo_pos, battery_m = self.battery_m,
                   battery_pos = self.battery_pos, p_pax = self.p_pax)
        reactionsCruise = self.loads.equilibriumCruise([self.pos, self.dragd], [self.pos, self.liftd],
                                                  [self.pos, [self.Mac / self.span]*len(self.pos)], self.wingWeight)
        reactionsVTO = self.loads.equilibriumVTO(wingWeight)
        lift, wgt = self.loads.internalLoads([self.pos, self.dragd], [self.pos, self.liftd],
                                        [self.pos, [self.Mac / self.span]*len(self.pos)], wingWeight)
        
        
        VxVTO, MyVTO = self.loads.internalLoadsVTO(wingWeight)
        
        coords, o_cr, tau_cr, Ymcr = self.loads.stressesCruise()
        coords, o_VTO, tau_VTO, YmVTO = self.loads.stressesVTO()

        (self.omin, self.omax), (self.taumin, self.taumax) = WingLoads.extreme(coords, o_cr), WingLoads.extreme(coords, tau_cr)
        self.Ymin, self.Ymax = WingLoads.extreme(coords, Ymcr)
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
            print(f"Mass of wing: {self.loads.mass(self.matsk)} kg")
            print(f"{nStrT, nStrB, 1e3*thicknessOfSkin, 1e3*thicknessOfSpar = }")
            if omin[1] > 0:
                raise StructuralError("Positive Compression Stress Encountered: " + str(omin[1]))
            if Ymax[1] < omax[1]:
                raise StructuralError("Von Mises stress less than normal stress")
            if Ymax[1] < taumax[1]:
                raise StructuralError("Von Mises stress less than shear stress")
            critbuckling = self.compute_buckling(self.matstr, self.matsk)
            cycles = self.compute_fatigue(self.matsk)
            yieldMargin, bucklingmargin = self.matsk.oy / Ymax[1], abs(critbuckling / omin[1])
            print(f"{critbuckling*1e-6, self.matsk.oy*1e-6 = }")
            print(f"{omin[1]*1e-6, Ymax[1]*1e-6, taumin[1]*1e-6 = }")
            print(f"{list(omin[0]), list(Ymax[0]), list(taumin[0]) = }")
            if omin[1] <= -critbuckling or Ymax[1] >= self.matsk.oy:
                print("Fail\n")
                if bucklingmargin > yieldMargin:
                    if abs(Ymax[0][0] - root.b/2) < 1e-7 or abs(Ymax[0][0] + root.b/2) < 1e-7:
                        thicknessOfSpar += 0.0001
                    elif abs(Ymax[0][1] - root.h/2) < 1e-7 or abs(Ymax[0][1] + root.h/2) < 1e-7:
                        thicknessOfSkin += 0.0001
                    else:
                        raise StructuralError(f"Coordinates not on wingbox: {Ymax[0]}")
                else:
                    nStrT += 1

            elif 1 < bucklingmargin < 1.5 and 1 < yieldMargin < 1.5:
                if self.cycles < 15*365*4:
                    raise StructuralError(f"Fatigue Life too low: {self.cycles}")
                else:
                    break
            else:
                print("Success\n")
                if bucklingmargin > yieldMargin:
                    nStrT -= 1
                else:
                    if abs(Ymax[0][0] - root.b/2) < 1e-7 or abs(Ymax[0][0] + root.b/2) < 1e-7:
                        thicknessOfSkin -= 0.0001
                    elif abs(Ymax[0][1] - root.h/2) < 1e-7 or abs(Ymax[0][1] + root.h/2) < 1e-7:
                        thicknessOfSpar -= 0.0001

        self.nStrT, self.nStrB, self.thicknessOfSkin, self.thicknessOfSpar = nStrT, nStrB, thicknessOfSkin, thicknessOfSpar
        return nStrT, nStrB, thicknessOfSkin, thicknessOfSpar

    plotNVMcruise = lambda self: InternalLoading(0, self.span/2, Vx = self.loads.Vx, Vy = self.loads.Vy,
                                                Mx = self.loads.Mx, My = self.loads.My, T = self.loads.T)

    plotNVMVTOL = lambda self: InternalLoading(0, self.span/2, Vx = self.loads.ViVx, My = self.loads.ViMy)
    
    plotFatigue = lambda self: DrawFatigue(self.tfat, self.fatcyc)
