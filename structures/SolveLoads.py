from Analysis import Stringer, WingBox, WingStructure
from Equilibrium import PointLoad, Moment, RunningLoad, EquilibriumEquation, DistributedMoment
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from MathFunctions.Mechanics import StepFunction
import rainflow

class Engines:
    def __init__(self, ThrustHover, ThrustCruise, positions: list[float, int], weight):
        self.n, self.Thover, self.Tcruise = len(positions), ThrustHover, ThrustCruise
        self.pos = positions
        self.w = weight
    __repr__ = __str__ = lambda self: "Engines(" + ', '.join(f"{k}={self.__dict__[k]}" for k in self.__dict__) + ")"

class WingLoads:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.wing, self.acp = [None]*2
        self.Fx, self.Fy, self.Fz, self.Mx, self.My, self.Mz = [None]*6
        self.RFx, self.RFy, self.RFz, self.RMx, self.RMy, self.RMz = [None]*6
        self.VFx, self.VMy, self.VMz = [None]*3
        self.ViVx, self.ViMy = [None]*2
        
        self.box = WingBox(self.tsk, self.tsp, self.frac, self.toc)
        self.box.StrPlacement(self.nStrT, self.nStrB, self.StrA)
        self.wing = WingStructure(self.span, self.taper, self.cr, self.box)
        self.acp = (self.xac - 0.45) * self.mac # Redefine
        
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    __getitem__ = lambda self, key: self.__dict__[key]

    __repr__ = __str__ = lambda self: "Wingloads(" + ', '.join(f"{k}={self.__dict__[k]}" for k in self.__dict__) + ")"

    def equilibriumCruise(self, dragDistr, liftDistr, macDistr, wingWeight):
        acp = self.acp
        Thrusts = [PointLoad([-self.engines.Tcruise, -self.engines.w, 0], [-0.45*self.wing(p).b/self.frac, 0, p]) \
                   for p in self.engines.pos] # Redefine x, y
        Drag = RunningLoad([dragDistr[1], [0]*len(dragDistr[1])], dragDistr[0], axis=2, poa=(acp, 0))
        Lift = RunningLoad([[0]*len(liftDistr[1]), liftDistr[1]], liftDistr[0], axis=2, poa=(acp, 0))
        Mac = DistributedMoment(values=[[0, 0, mom] for mom in macDistr[1]], positions=macDistr[0])
        weights = RunningLoad(values=[[0]*2, [-wingWeight / self.span]*2], positions=[0, self.span/2], axis=2)
        eqn = EquilibriumEquation(kloads=[Lift, weights, Drag, Mac] + Thrusts,
                                 ukloads=[PointLoad([1, 0, 0], [0, 0, 0]), PointLoad([0, 1, 0], [0, 0, 0]),
                                          PointLoad([0, 0, 1], [0, 0, 0]), Moment([1, 0, 0]),
                                          Moment([0, 1, 0]), Moment([0, 0, 1])])

        eqn.SetupEquation()
        self.RFx, self.RFy, self.RFz, self.RMx, self.RMy, self.RMz = solved = eqn.SolveEquation()
        return solved
    
    def equilibriumVTO(self, wingWeight):
        Thrusts = [PointLoad([-self.engines.Thover + self.engines.w, 0, 0],
                             [-0.45*self.wing(p).b/self.frac, 0, p]) for p in self.engines.pos] # Redefine x, y
        weights = RunningLoad(values=[[wingWeight / self.span]*2, [0]*2], positions=[0, self.span/2], axis=2)
        eqtn = EquilibriumEquation(kloads=[weights] + Thrusts,
                                  ukloads=[PointLoad([1, 0, 0], [0, 0, 0]), Moment([0, 1, 0]), Moment([0, 0, 1])])
        eqtn.SetupEquation()
        self.VFx, self.VMy, self.VMz = eqtn.SolveEquation()
        return self.VFx, self.VMy, self.VMz
    
    def internalLoads(self, dragDistr, liftDistr, macDistr, wingWeight):
        if not any([self.RFx, self.RFy, self.RFz, self.RMx, self.RMy, self.RMz]):
            self.equilibriumCruise(dragDistr, liftDistr, macDistr, wingWeight)

        lin = LinearRegression()
        poly = PolynomialFeatures(degree=20)
        X = poly.fit_transform(dragDistr[0].reshape(-1, 1))
        lin.fit(X, np.array([dragDistr[1], liftDistr[1], macDistr[1]]).T)
        dragcoef, liftcoef, momcoef = lin.coef_
        interd, interl, interm = lin.intercept_
    
        drag = StepFunction([[dragcoef[i], 0, i] for i in range(len(dragcoef))]) + interd
        lift = StepFunction([[liftcoef[i], 0, i] for i in range(len(liftcoef))]) + interl
        Mac = StepFunction([[momcoef[i], 0, i] for i in range(len(momcoef))]) + interm
        Thrust = StepFunction([[-self.engines.Tcruise, p, 0] for p in self.engines.pos])
        ThrustW = StepFunction([[-self.engines.w, p, 0] for p in self.engines.pos])
        MThrust = StepFunction([[0.45*self.wing(p).b * self.engines.w / self.frac, p, 0] for p in self.engines.pos])
    
        wgt = StepFunction([[-wingWeight / self.span, 0, 0]])
        self.Vy = -(lift + wgt).integral(self.RFy) - ThrustW
        self.Vx = -(Thrust + drag.integral() + self.RFx)
        self.T = -(Mac + lift * self.acp).integral(self.RMz) - MThrust
        self.My, self.Mx = self.Vx.integral(self.RMy), self.Vy.integral(-self.RMx)
        return lift, wgt

    def internalLoadsVTO(self, wingWeight):
        wgt = StepFunction([[wingWeight / self.span, 0, 0]]) # Fx
        Thrusts = StepFunction([[-self.engines.Thover+self.engines.w, p, 0] for p in self.engines.pos]) # Fx
        self.ViVx = Vx = -(Thrusts + wgt.integral() + self.VFx)
        self.ViMy = My = Vx.integral(self.VMy)
        return Vx, My
    
    def stresses(self):
        root = self.wing(0)
        tauv = root.tau(0, root.h/2, Vx=self.ViVx(0), Vy=0, T=0)
        ldt = dict(Vx=self.Vx(0), Vy=self.Vy(0), T=self.T(0))
        ytaucmax = StepFunction.optimize(lambda y: root.tau(root.b/2, y, **ldt), -root.h/2, root.h/2)
        tauc1 = root.tau(-root.b/2, ytaucmax, **ldt)
        
        xtaucmax = StepFunction.optimize(lambda x: root.tau(x, root.h/2, **ldt), -root.b/2, root.b/2)
        tauc2 = root.tau(xtaucmax, -root.h/2, Vx=self.Vx(0), Vy=self.Vy(0), T=self.T(0))
        tauc = [tauc1, tauc2][np.argmax([abs(tauc1), abs(tauc2)])]
        
        ov = root.o(root.b/2, 0, Mx=0, My=self.ViMy(0))
        lds = dict(My=self.My(0), Mx=self.Mx(0))
        yocmax = StepFunction.optimize(lambda y: root.o(-root.b/2, y, **lds), -root.h/2, root.h/2)
        oc1 = root.o(-root.b/2, ytaucmax, **lds)
        xocmax = StepFunction.optimize(lambda x: root.o(x, root.h/2, **lds), -root.b/2, root.b/2)
        oc2 = root.o(xocmax, root.h/2, **lds)
        oc = [oc1, oc2][np.argmax([abs(oc1), abs(oc2)])]
        stressc = [(root.tau(x, root.h/2, **ldt), root.o(x, root.h/2, **lds)) for x in np.linspace(-root.b/2, root.b/2, 100)] + \
                  [(root.tau(-root.b/2, y, **ldt), root.o(-root.b/2, y, **lds)) for y in np.linspace(-root.h/2, root.h/2, 100)]
        
        stressv = [(root.tau(x, root.h/2, Vx=self.ViVx(0)), root.o(x, root.h/2, My=self.ViMy(0))) for x in np.linspace(-root.b/2, root.b/2, 100)] + \
                  [(root.tau(-root.b/2, y, Vx=self.ViVx(0)), root.o(-root.b/2, y, My=self.ViMy(0))) for y in np.linspace(-root.h/2, root.h/2, 100)]

        Yc, Yv = [[(3*tau ** 2 + o ** 2) ** 0.5 for tau, o in stres] for stres in [stressc, stressv]]
        return tuple([max([a[0] for a in stressc]), max([a[0] for a in stressv]),
                     max([a[1] for a in stressc]), max([a[1] for a in stressv]),
                     np.max(Yc), np.max(Yv)])

class Fatigue:
    def __init__(self, Sground, Stakeoff, Scruise, airTime, turnOver, takeOffTime, mat):
        self.Sg, self.Sto, self.Scr, self.tAir, self.tTO = Sground, Stakeoff, Scruise, airTime, takeOffTime
        self.tot = turnOver
        self.cyc, self.df, self.ts = [None]*3
        self.mat = mat

    def determineCycle(self):
        self.ts = np.linspace(0, self.tAir + self.tot, 1000)
        gag, tg = [], self.tot / 2
        for t in self.ts:
            acoustic = 0.2 * np.sum(np.sin(2*np.pi * t / np.arange(0.001/3600, 0.01/3600, 0.001/3600))) # noise in the given frequency range
            turbulence = np.sum(np.sin(2*np.pi * t / np.arange(0.1/3600, 10/3600, 0.1/3600))) # same here
            taxi = np.sum(np.sin(2*np.pi * t / np.arange(0.05/3600, 1/3600, 0.05/3600))) # and here, all frequencies taken from the textbook - Schijve Ch 9
            if t < tg or t > self.tAir + tg:
                gag.append(self.Sg + (taxi if tg > t > 0.5 * tg or self.tAir + tg < t < self.tAir + 1.5 * tg else 0))
            elif tg + 0.5 <= t <= self.tAir + tg - 0.5:
                gag.append(self.Scr + acoustic + (turbulence if tg + 1 > t or t > self.tAir + tg - 1 else 0))
            else:
                gag.append(self.Sto + acoustic + turbulence)
        self.cyc = np.array(gag)
        return self.ts, self.cyc

    def getCycles(self):
        df = pd.DataFrame(data=list(rainflow.extract_cycles(self.cyc)),
                              columns='dS, Sm, count, ti, tf'.split(', '))
        self.df = df[df['count'] != 0]
        return self.df
    
    def MinersRule(self, paris=False, w=None, ar=(None, None)):
        Ns = np.array([self.mat.ParisFatigueN(dS, w, *ar) if paris else self.mat.BasquinLaw(dS) for dS in self.df.dS])
        nCycles = self.df['count'] / Ns
        return 1 / nCycles.sum()
