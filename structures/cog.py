from pandas import read_excel
import numpy as np
import json
from constants import *
from analysis import get_data

def MakeError(message, defarg2=None):
    class MassError(Exception):
        def __init__(self, arg1, arg2=defarg2):
            super().__init__(message(arg1, arg2))
        __module__ = 'builtins'
    return MassError

MassErrorMessage = lambda W, kilos: f'Negative and/or Unrealistic Mass Encountered ({W} {"kg" if kilos else "lbs"})'
LPEMessage = lambda a, inches: f'Someone Fell Off The Aircraft Mid-Flight ({a} {"inches" if inches else "m"})'

LongitudinalPositionError = MakeError(LPEMessage, True)
MassError = MakeError(MassErrorMessage, True)
FuelFlowError = MakeError(lambda ff, t: f'Double Check Your Fuel Flow, {ff} (at time {t})')

class Mass:
    def __init__(self, weight, arm, kilos=False, inches=True):
        self.w, self.a = weight * (1 if kilos else lbs), arm * (inch if inches else 1)
        self.verify()

    def verify(self):
        arm = self.a / inch
        if self.w < 0 or self.w > 4.5e3:
            raise MassError(self.w)
        if arm < 70 or arm > 340:
            raise LongitudinalPositionError(arm)
        return True

    def update(self, W, kilos=True):
        self.w = W * (1 if kilos else lbs)
        self.verify()
    
    def rel_update(self, dW, kilos=True):
        self.update(self.w + dW * (1 if kilos else lbs))
        self.verify()

    def move(self, position, inches=False):
        self.a = position * (inch if inches else 1)
    
    def rel_move(self, dposition, inches=False):
        self.move(self.a + dposition * (inch if inches else 1))

    moment = lambda self: self.w * self.a

    __str__ = __repr__ = lambda self: f'Mass(weight={self.w}, arm={self.a})'

class Fuel(Mass):
    def __init__(self, weight, arm, kilos=False, inches=True):
        fuels = ''.join(['298.16591.18879.081165.421448.401732.532014.802298.842581.',
            '922866.303150.183434.523718.524003.234287.764572.244856.565141',
            '.165425.645709.905994.046278.476562.826846.967131.00',
            '7415.337699.607984.348269.068554.058839.049124.809410.629696.979983.4010,270.0810,556.8410,84',
            '3.8711,131.0011,418.2011,705.5011,993.3112,281.1812,569.0412,8',
            '56.8613,144.7313,432.4813,720.5614,008.4614,320.34']).replace(',', '')
        self.table, mass = [], 0
        while len(fuels) > 0:
            nex = fuels[:fuels.index('.') + 3]
            fuels = fuels.replace(nex, '')
            mass += 100 if len(fuels) > 0 else 108
            self.table.append([mass * lbs, float(nex) * 45.3592 * inch])
        super().__init__(weight, arm, kilos, inches)

    def verify(self):
        if not super().verify() or self.w > self.table[-1][0]:
            raise MassError(self.w)
        return True

    def moment(self):
        self.verify()
        for i, (m, M) in enumerate(self.table):
            if m < self.w and self.table[i+1][0] >= self.w:
                m0, M0 = m, M
                m1, M1 = self.table[i+1]
                break
        self.a = (M0 + (M1 - M0) * (self.w - m0) / (m1 - m0)) / self.w
        return super().moment()

    def burn(self, t, FF0, FF1=None, t1=-1, t0=0):
        if all(v >= -1 for v in [t, FF0, t1, t0]):
            if FF1 is None or (FF1 >= 0 and t1 != -1):
                self.w -= (FF0 * t + (0 if FF1 is None else (FF1 - FF0) / 2) * (t - t0) ** 2 / (t1 - t0))
                self.verify()
                return self.w
        raise FuelFlowError(FF1, t1)

class Plane:
    def __init__(self, people={}, fuel=Fuel(0, 100), baggage=[], MAC=80.98, lw=261.56, BEM=Mass(9165, 291.65)):
        self.people, self.fuel, self.baggage = people, fuel, baggage
        self.c, self.lw, self.structure = MAC * inch, lw * inch, BEM
        self.seats = [x - lw for x in [131]*2 + [214]*2 + [251]*2 + [288]*2 + [170]]
        self.history = {p: [] for p in ('fuel', 'mass', 'cog')}
        self._record()

    @staticmethod
    def read(data='../Data/flightdata.xlsx'):
        df = read_excel(data)
        weights = {w[0].replace(':', ''): float(w[7]) for w in df.iloc[6:15].values}
        block_fuel = Fuel(float(df.iloc[16].values[3]), 287.58) # Revise Locations if necessary
        xcgs = {'pilot': 131, 'observer 1': 214, 'observer 2': 251, 'observer 3': 288, 'co-ordinator': 170}
        people = {person: Mass(weights[person], xcgs[[w for w in xcgs if w in person][0]], True) for person in weights}
        return Plane(people, block_fuel, baggage=[Mass(0, 74), Mass(0, 321), Mass(0, 338)]) # Change if Baggage

    @staticmethod
    def test(data='../Data/InitialData.json'):
        dt = json.load(open(data, 'r'))
        weights = {p: dt['Payload'][p]['Weight'] for p in dt['Payload']}
        xcgs = {'pilot': 131, 'observer 1': 214, 'observer 2': 251, 'observer 3': 288, 'coordinator': 170}
        people = {p: Mass(weights[p], xcgs[[w for w in xcgs if w in p.lower()][0]], True) for p in weights}
        fuel = Fuel(dt['Aircraft']['Fuel Weight'], 287.58)
        return Plane(people, fuel, baggage=[Mass(0, 74), Mass(0, 321), Mass(0, 338)])

    BEM, cgBEM = lambda self: self.structure.w, lambda self, pC=False:  (self.structure.a - self.lw) / (self.c if pC else 1)

    _mass = lambda self, lst: sum(m.w for m in lst)

    _cg = lambda self, lst, pC=False: (sum(m.moment() for m in lst) / self._mass(lst) - self.lw) / (self.c if pC else 1)

    ZFM = lambda self: self._mass([self.structure] + self.ppl + self.baggage)

    cgZFM = lambda self, pC=False: self._cg([self.structure] + self.ppl + self.baggage, pC)

    mass = lambda self: self._mass([self.structure] + self.ppl + self.baggage + [self.fuel])

    cg = lambda self, pC=False: self._cg([self.structure] + self.ppl + self.baggage + [self.fuel], pC)

    def _record(self):
        self.ppl = list(self.people.values())
        self.history['mass'].append(self.mass())
        self.history['cog'].append(self.cg())
        self.history['fuel'].append(self.fuel.w)

    def move(self, person, position, inches=False):
        try:
            mass1 = self.mass()
            self.people[person].move(position + self.lw * (1/inch if inches else 1), inches)
            mass2 = self.mass()
            self._record()
            if not mass1 == mass2:
                raise Exception('Incorrect')
        except KeyError:
            pp = ', '.join(list(self.people.keys()))
            raise NameError('There is nobody with that name. People on board include:\n' + pp)
        except:
            raise LongitudinalPositionError(self.people[person].a, False)

    def rel_move(self, person, dposition, inches=False):
        try:
            mass1 = self.mass()
            self.people[person].rel_move(dposition, inches)
            mass2 = self.mass()
            self._record()
            if not mass1 == mass2:
                raise Exception('Incorrect')
        except KeyError:
            pp = ', '.join(list(self.people.keys()))
            raise NameError('There is nobody with that name. People on board include:\n' + pp)
        except:
            raise LongitudinalPositionError(self.people[person].a, False)

    def burn_fuel(self, t, FF0, FF1=None, t1=-1, t0=0):
        self.fuel.burn(t, FF0, FF1, t1, t0)
        self._record()
        return self.fuel.w

    def use_fuel(self, dW, kilos=True):
        self.fuel.rel_update(dW=-dW, kilos=kilos)
        self._record()
        return self.fuel.w

    muc, mub = lambda self, rho: self.mass() / (rho * S * c), lambda self, rho: self.mass() / (rho * S * b)

    __str__ = __repr__ = lambda self: f'Plane(m = {round(self.mass(), 3)} kg, xcg = {round(self.cg(1), 3)} c)'

def Weight(Fused):
    masses = []
    num = False
    if type(Fused) in [int, float, np.float64, np.float32, np.uint8]:
        Fused, num = [Fused], True
    for fi in Fused:
        plane = Plane.read()
        plane.use_fuel(fi, kilos=True)
        masses.append(plane.mass() * g_0)
    return masses[0] if num else np.array(masses)

if __name__ == '__main__':
    from pandas import DataFrame

    # cessna = Plane.read('../Data/flightdata.xlsx') # Load Reference Data. Includes Mass of Passengers, Pilots, Baggage and Fuel.
    # dcg = lambda cog1, cog2: f'Difference in c.o.g: {abs(cog2 - cog1)} m towards the {"tail" if cog2 > cog1 else "nose"} of the aircraft'
    # dm = lambda m1, m2: f'ΔMass = {m1 - m2} kg' # Losing Mass = Positive Change
    #
    # ṁf, tb, RM, cog1 = 4, 150, cessna.mass(), cessna.cg() # kg / s, s, kg, m
    # print(f'Before {tb} s of a constant {ṁf} kg/s FF:\n{cessna = }')
    # print(f'cgR = {cog1} m, cgZF = {cessna.cgZFM()} m, cgBE = {cessna.cgBEM()} m')
    # print(f'{RM = } kg, ZFM = {cessna.ZFM()} kg, BEM = {cessna.BEM()} kg', end='\n\n')
    #
    # cessna.burn_fuel(t=tb, FF0=ṁf)
    # cog2 = cessna.cg()
    # m2 = cessna.mass()
    # print(f'After burning {ṁf*tb=} kg of fuel:\n{cessna = }\n{dcg(cog1, cog2)}\n{dm(RM, m2)}', end='\n\n')
    #
    # person, seat = 'co-ordinator', 5 # Move the co-ordinator to seat 5 (ie. Δx = 251 - 170 in.)
    # cessna.move(person, position=cessna.seats[seat-1], inches=True)
    # print(f'After moving the {person} to seat {seat}:\n{cessna = }\n{dcg(cog2, cessna.cg())}\n{dm(m2, cessna.mass())}', end='\n\n')
    # print(f'See History (fuel and aircraft mass in kg, c.o.g. in m):\n{DataFrame(cessna.history)}')
    plane = Plane.test()
    print(f'{plane.BEM() * kg, (plane.cgBEM()+plane.lw) / inch = }')
    print(f'{plane.ZFM() * kg, (plane.cgZFM()+plane.lw) / inch = }')
    print(f'{plane.fuel = }')
    print(f'Ramp: {plane.mass() * kg, (plane.cg()+plane.lw) / inch = }')
    ppl = {p: Mass(m.w*kg, m.a/inch, True, False) for p, m in zip(plane.people.keys(), plane.people.values())}
    print({p: ppl[p].moment() for p in ppl})
    print(f'Payload: {ppl}\nsums:{sum([m.w for m in ppl.values()])} lbs {sum([m.moment() for m in ppl.values()])} lbs-inch')
