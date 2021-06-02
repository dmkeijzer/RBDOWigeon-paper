import numpy as np
from MathFunctions.Trigonometry import pi
from MathFunctions.Mechanics import StepFunction
import pandas as pd

class Stringer:
    def __init__(self, area = 0.001, point = (0, 0)):
        self.a, (self.x, self.y) = area, point
        
    __repr__ = __str__ = lambda self: f"Stringer(Area={str(self.a)}, Position={str(self.x), str(self.y)})"
    
    Ixx = lambda self: self.a * self.y**2
    Iyy = lambda self: self.a * self.x**2

class ZStringer(Stringer):
    def __init__(self, area = 0.001, point = (0, 0), bflange = 0.05, tflange = 0.05, vflange = 0.05, tstr = 0.001):
        super.__init__()
        self.bflange, self.tflange, self.vflange, self.t = bflange, tflange, vflange, tstr

    a = lambda self: ((self.tflange - self.t) + (self.bflange - self.t) + (self.vflange - (2 * self.t))) * self.t
    
    def cripplingStress(self, E, v, sigma_y):
        alpha, n = 0.8, 0.6
        ccstress1 = 0.8 * (0.425/sigma_y * (np.pi**2 * E / (12 * (1 - v**2))) * (self.t / (self.bflange - self.t))**2) ** (1 - n) * sigma_y
        ccstress2 = 0.8 * (0.425/sigma_y * (np.pi**2 * E / (12 * (1 - v**2))) * (self.t / (self.tflange - self.t))**2) ** (1 - n) * sigma_y
        ccstress3 = 0.8 * (4/sigma_y * (np.pi**2 * E / (12 * (1 - v**2))) * (self.t / (self.vflange - self.t))**2) ** (1 - n) * sigma_y
        return (ccstress1 * self.t * (self.bflange - self.t) 
                + ccstress2 * self.t * (self.tflange - self.t)
                + ccstress1 * self.t * (self.vflange - 2*self.t)) / self.a()
    
class HatStringer(Stringer):
    def __init__(self, area = 0.001, point = (0, 0), bflange1 = 0.05, bflange2 =0.05, tflange = 0.05, vflange = 0.05, tstr = 0.001):
        super.__init__()
        self.bflange1, self.bflange2, self.tflange, self.vflange, self.t = bflange1, bflange2, tflange, vflange, tstr

    a = lambda self: ((self.tflange - self.t) + (self.bflange1 - self.t) + (self.bflange2 - self.t) + 2*(self.vflange - (2 * self.t))) * self.t
    
    def cripplingStress(self, E, v, sigma_y):
        alpha, n = 0.8, 0.6
        ccstress1 = 0.8 * (0.425/sigma_y * (np.pi**2 * E / (12 * (1 - v**2))) * (self.t / (self.bflange1 - self.t))**2) ** (1 - n) * sigma_y
        ccstress5 = 0.8 * (0.425/sigma_y * (np.pi**2 * E / (12 * (1 - v**2))) * (self.t / (self.bflange2 - self.t))**2) ** (1 - n) * sigma_y
        ccstress24 = 0.8 * (4/sigma_y * (np.pi**2 * E / (12 * (1 - v**2))) * (self.t / (self.vflange - self.t))**2) ** (1 - n) * sigma_y
        ccstress3 = 0.8 * (4/sigma_y * (np.pi**2 * E / (12 * (1 - v**2))) * (self.t / (self.tflange - self.t))**2) ** (1 - n) * sigma_y
        return (ccstress1 * self.t * (self.bflange1 - self.t) 
                + ccstress5 * self.t * (self.bflange2 - self.t)
                + 2* ccstress24 * self.t * (self.vflange - 2*self.t) + ccstress3 * self.t * (self.tflange - 2*self.t)) / self.a()
    
    
class WingBox:
    def __init__(self, thicknessOfSkin, thicknessOfSpar, base, height, stringers = []):
        self.b, self.h, self.tsk, self.tsp = base, height, thicknessOfSkin, thicknessOfSpar
        self.str = stringers
    
    __str__ = __repr__ = lambda self: \
    f"Wingbox(Height={str(self.h)}, Base={str(self.b)}, Tsk = {str(self.tsk)}, Tsp = {str(self.tsp)}, Stringers = {len(self.str)})"
    
    Area = lambda self: self.b * self.h - (self.b - 2 * self.tsp) * (self.h - 2 * self.tsk) + sum(s.a for s in self.str)

    Ixx = lambda self: (self.tsp * self.h ** 3 + self.b * self.tsk ** 3) / 6 + (self.tsk * self.b * self.h ** 2) / 2 + sum(s.Ixx() for s in self.str)
    
    Iyy = lambda self: (self.tsk ** 3 * self.h + self.b ** 3 * self.tsp) / 6 + (self.tsp * self.h * self.b ** 2) / 2 + sum(s.Iyy() for s in self.str)
    
    Vc = Ixy = lambda self: 0
    
    def StrPlacement(self, nstr_top:int , nstr_bottom:int , area):
        topstringers = [Stringer(area, point = (i*self.b/(nstr_top + 1) - self.b/2, self.h/2)) for i in range(1, nstr_top+1)]
        bottomstringers = [Stringer(area, point = (i*self.b/(nstr_bottom + 1) - self.b/2, -self.h/2)) for i in range(1, nstr_bottom+1)]
        self.str = self.str.copy() + topstringers + bottomstringers
        
    def Vshear(self, Vy, x, y):
        Ixx = self.Ixx()
        inrge = lambda l1, u1, l2, u2: l1 <= x <= u1 and l2 <= y <= u2
        vit = - Vy * self.tsp / Ixx if (-self.b/2 <= x <= -self.b/2 + self.tsp) or (self.b/2 - self.tsp <= x <= self.b/2) else - Vy * self.tsk / Ixx
        if inrge(0, self.b/2, -self.h/2, -self.h/2 + self.tsk):
            return vit * (-self.h * x / 2)
        elif inrge(self.b/2-self.tsp, self.b/2, -self.h/2, self.h/2):
            s = self.h/2 + y
            return vit * (0.5 * s * s - self.h * s / 2) + self.Vshear(Vy, self.b/2, -self.h/2)
        elif inrge(-self.b/2, self.b/2, self.h/2-self.tsk, self.h/2):
            s = self.b/2 - x
            return vit * (self.h*s/2) + self.Vshear(Vy, self.b/2, self.h/2)
        elif inrge(-self.b/2, -self.b/2+self.tsp, -self.h/2, self.h/2):
            s = self.h/2 - y
            return vit * (-0.5 * s * s + self.h * s / 2) + self.Vshear(Vy, -self.b/2, self.h/2)
        elif inrge(-self.b/2, 0, -self.h/2, -self.h/2+self.tsk):
            return vit * (-self.h * (x + self.b/2) / 2) + self.Vshear(Vy, -self.b/2, -self.h/2)
        else:
            raise ValueError(f"Invalid Coordinates Supplied: {(x, y) = }")

    def Hshear(self, Vx, x, y):
        Iyy = self.Iyy()
        inrge = lambda l1, u1, l2, u2: l1 <= x <= u1 and l2 <= y <= u2
        vit = - Vx * self.tsp / Iyy if (-self.b/2 <= x <= -self.b/2 + self.tsp) or (self.b/2 - self.tsp <= x <= self.b/2) else - Vx * self.tsk / Iyy
        if inrge(-self.b/2, -self.b/2+self.tsp, -self.h/2, 0):
            return vit * (self.b * y / 2)
        elif inrge(-self.b/2, self.b/2, -self.h/2, -self.h/2+self.tsk):
            s = x + self.b/2
            return vit * (0.5 * s * s - self.b * s / 2) + self.Hshear(Vx, -self.b/2, -self.h/2)
        elif inrge(self.b/2 -self.tsp, self.b, -self.h/2, self.h/2):
            return vit * (self.b * (y + self.h/2) / 2) + self.Hshear(Vx, self.b/2, -self.h/2)
        elif inrge(-self.b/2, self.b/2, self.h/2-self.tsk, self.h/2):
            s = -x + self.b/2
            return vit * (-0.5 * s * s + self.b * s / 2) + self.Hshear(Vx, self.b/2, self.h/2)
        elif inrge(-self.b/2, -self.b/2+self.tsp, 0, self.h/2):
            return vit * (-self.b * (self.h/2-y) / 2) + self.Hshear(Vx, -self.b/2, self.h/2)
        else:
            raise ValueError(f"Invalid Coordinates Supplied: {(x, y) = }")
    
    q = lambda self, x, y, Vx=0, Vy=0, T=0: self.Vshear(Vy, x, y) + self.Hshear(Vx, x, y) + T / (2 * self.Area())
    tau = lambda self, x, y, Vx=0, Vy=0, T=0: self.q(x, y, Vx, Vy, T) / (self.tsp if \
        (-self.b/2 <= x <= -self.b/2 + self.tsp) or (self.b/2 - self.tsp <= x <= self.b/2) else self.tsk)
    
    o = lambda self, x, y, Mx=0, My=0: My * x / self.Iyy() + Mx * y / self.Ixx()

class WingStructure:
    def __init__(self, span, taper, rootchord, wingbox):
        self.span, self.taper, self.rc = span, taper, rootchord
        self.tc = self.rc * self.taper
        self.box = wingbox
    
    chord = lambda self, z: self.rc * (self.taper - 1) * z / (self.span/2) + self.rc if (0 <= z <= self.span/2) else None
    __call__ = lambda self, z: WingBox(self.box.tsk, self.box.tsp, self.box.b*self.chord(z), self.box.h*self.chord(z), self.box.str)
