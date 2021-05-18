import pandas as pd
from scipy.integrate import quad
from MathFunctions.Trigonometry import cos, pi

class Material:
    def __init__(self, E, density, o_yield, o_ult, Paris=(None, None), name=None, poisson=0.33, **others):
        self.E, self.rho, self.oy, self.oult, self.v = E, density, o_yield, o_ult, poisson
        self.C, self.m = Paris
        self.props = others
        self.name = name
    
    __repr__ = __str__ = lambda self: (self.name if self.name else "Material")+f"(E={self.E}, ρ={self.rho}, σy={self.oy}, σult={self.oult})"
    
    def buckling(self, shorterSideOfSkin, skinThickness):
        C = 5.41 # SSCS Support
        b = shorterSideOfSkin
        t = skinThickness
        return C * pi * pi * self.E * (t / b) ** 2 / (12 * (1 - self.v ** 2))
    
    @staticmethod
    def load(file='materials.csv', material='Al 6061', Condition='T6'):
        df = pd.read_csv(file)
        check = df[df['Material'] == material]
        if len(check) == 0:
            raise KeyError(f'No {material = } could be found')
        elif len(check) == 1:
            mat = check.iloc[0]
        else:
            mat = check[check['Condition'] == Condition].iloc[0]
        return Material(mat.E, mat.rho, mat.oyield, mat.oult, (mat.ParisA, mat.Parism), mat.Material, mat.v)
    
    @staticmethod
    def beta(aow, center=True): 
        return (1/cos(pi * aow)) ** 0.5 if center else 1.1215 # pg 131

    @staticmethod
    def StressConcentration(beta, a, o):
        return beta * o*1e-6 * (pi * a) ** 0.5
    
    def ParisFatigueN(self, dS, w, ai, af):
        def integrand(a):
            beta = self.beta(a/w)
            return 1 / self.StressConcentration(beta, a, dS)**self.m
        N = (1/self.C) * quad(integrand, ai, af)[0]
        return N
