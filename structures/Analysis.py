import numpy as np
from MathFunctions.Trigonometry import pi
from MathFunctions.Mechanics import StepFunction
import pandas as pd

class WingBox:
    def __init__(self, thickness, base, height, material):
        self.b, self.h, self.t = base, height, thickness
        self.mat = material
        self.beta = {float(d.split('\t')[0]): float(d.split('\t')[1]) for d in """1.0\t0.141
1.5	0.196
2.0	0.229
2.5	0.249
3.0	0.263
4.0	0.281
5.0	0.291
6.0	0.299
10.0\t0.312
10000\t0.333""".split('\n')}
    
    Area = lambda self: self.b * self.h - (self.b - 2 * self.t) * (self.h - 2 * self.t)

    Ixx = lambda self: (self.t * self.h ** 3 + self.b * self.t ** 3) / 6 + (self.t * self.b * self.h ** 2) / 2
    
    Iyy = lambda self: (self.t ** 3 * self.h + self.b ** 3 * self.t) / 6 + (self.t * self.h * self.b ** 2) / 2
    
    Vc = Ixy = lambda self: 0
    
    def Vshear(self, Vy, x, y):
        Ixx = self.Ixx()
        inrge = lambda l1, u1, l2, u2: l1 <= x <= u1 and l2 <= y <= u2
        vit = - Vy * self.t / Ixx
        if inrge(0, self.b/2, -self.h/2, -self.h/2 + self.t):
            return vit * (-self.h * x / 2)
        elif inrge(self.b/2-self.t, self.b/2, -self.h/2, self.h/2):
            s = self.h/2 + y
            return vit * (0.5 * s * s - self.h * s / 2) + self.Vshear(Vy, self.b/2, -self.h/2)
        elif inrge(-self.b/2, self.b/2, self.h/2-self.t, self.h/2):
            s = self.b/2 - x
            return vit * (self.h*s/2) + self.Vshear(Vy, self.b/2, self.h/2)
        elif inrge(-self.b/2, -self.b/2+self.t, -self.h/2, self.h/2):
            s = self.h/2 - y
            return vit * (-0.5 * s * s + self.h * s / 2) + self.Vshear(Vy, -self.b/2, self.h/2)
        elif inrge(-self.b/2, 0, -self.h/2, -self.h/2+self.t):
            return vit * (-self.h * (x + self.b/2) / 2) + self.Vshear(Vy, -self.b/2, -self.h/2)
        else:
            raise ValueError(f"Invalid Coordinates Supplied: {(x, y) = }")

    def Hshear(self, Vx, x, y):
        Iyy = self.Iyy()
        inrge = lambda l1, u1, l2, u2: l1 <= x <= u1 and l2 <= y <= u2
        vit = - Vx * self.t / Iyy
        if inrge(-self.b/2, -self.b/2+self.t, -self.h/2, 0):
            return vit * (self.b * y / 2)
        elif inrge(-self.b/2, self.b/2, -self.h/2, -self.h/2+self.t):
            s = x + self.b/2
            return vit * (0.5 * s * s - self.b * s / 2) + self.Hshear(Vx, -self.b/2, -self.h/2)
        elif inrge(self.b/2 -self.t, self.b, -self.h/2, self.h/2):
            return vit * (self.b * (y + self.h/2) / 2) + self.Hshear(Vx, self.b/2, -self.h/2)
        elif inrge(-self.b/2, self.b/2, self.h/2-self.t, self.h/2):
            s = -x + self.b/2
            return vit * (-0.5 * s * s + self.b * s / 2) + self.Hshear(Vx, self.b/2, self.h/2)
        elif inrge(-self.b/2, -self.b/2+self.t, 0, self.h/2):
            return vit * (-self.b * (self.h/2-y) / 2) + self.Hshear(Vx, -self.b/2, self.h/2)
        else:
            raise ValueError(f"Invalid Coordinates Supplied: {(x, y) = }")

    q = lambda self, x, y, Vx=0, Vy=0, T=0: self.Vshear(Vy, x, y) + self.Hshear(Vx, x, y) + T / (2 * self.Area())
    tau = lambda self, x, y, Vx=0, Vy=0, T=0: self.q(x, y, Vx, Vy, T) / self.t
    o = lambda self, x, y, Mx=0, My=0: My * x / self.Iyy() + Mx * y / self.Ixx()
    buckling = lambda self: self.mat.buckling(min(self.b, self.h), self.t)
    fatigue = lambda self, dS, ai, af: self.mat.ParisFatigueN(dS, self.b, ai, af)
    def J(self):
        a, b = max(self.b, self.h), min(self.h, self.b)
        minerr, closest = float('inf'), -1
        for val in self.beta:
            if abs(val - a/b) < minerr:
                minerr, closest = abs(val - a/b), self.beta[val]
        return closest * a * b ** 3

class WingStructure:
    def __init__(self, wingequation):
        WingLoads = wingequation.SolveEquation()
        self.RFx, self.RFy, self.RFz = WingLoads[:3]
        self.RMx, self.RMy, self.RMz = WingLoads[3:] # WingWeight, Lift, Drag, MomentAC, Thrust
        self.W, self.L, self.D, self.Mac, *self.T = wingequation.k

        self.N = self.Vx = self.Vy = self.Mz = self.Mx = self.My = None
        self.v = self.w = self.phi = None

    def compute_loading(self):
        self.N = StepFunction([[self.RFz, 0, 0]])
        qxzcoef = list(np.polyfit(self.W.p, self.W.v[0] + self.D.v[0] + self.L.v[0], 4))[::-1]
        qyzcoef = list(np.polyfit(self.W.p, self.W.v[1] + self.D.v[1] + self.L.v[1], 4))[::-1]
        qxz = StepFunction([[xi, 0, i] for i, xi in enumerate(qxzcoef)])
        qyz = StepFunction([[yi, 0, i] for i, yi in enumerate(qyzcoef)])
        self.Vx = StepFunction([[self.RFx, 0, 0]] + [[T.f[0], T.p[2], 0] for T in self.T]) + qxz.integral()
        self.Vy = StepFunction([[self.RFy, 0, 0]] + [[T.f[1], T.p[2], 0] for T in self.T]) + qyz.integral()
        self.Mz = self.L.pa[0] * qyz.integral() - self.L.pa[1] * qxz.integral() + self.RMz
        self.My, self.Mx = self.Vx.integral(-self.RMy), self.Vy.integral(self.RMx)
        return [self.N, self.Vx, self.Vy, self.Mx, self.My, self.Mz]

    def compute_deflections(self, E, Ixx, Iyy=None):
        Iyy = Ixx if Iyy is None else Iyy
        self.v = -self.My.integral().integral() / (E * Ixx)
        self.w = self.Mx.integral().integral() / (E * Iyy)
        return self.v, self.w

    def create_nvm(self, b):
        x = np.linspace(0, b/2, 100)
        df = pd.DataFrame({'z': x} | {ln: [lv(xi) for xi in x] for ln, lv in \
                            zip(('v', 'w', 'Mx', 'My', 'Mz', 'N', 'Vx', 'Vy'), 
                                (self.v, self.w, self.Mx, self.My, self.Mz, self.N, self.Vx, self.Vy))}) \
                                    .set_index('z')
        for col in df.columns:
            df.plot(y=col)
    
