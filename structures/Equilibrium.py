import numpy as np
from scipy.integrate import quad, dblquad

class PointLoad:
    def __init__(self, force, point):
        self.p = np.array(point)
        self.f = np.array(force)

    moment = lambda self: np.cross(self.p, self.f)

    momentx, momenty, momentz = [lambda self: self.moment()[i] for i in range(3)]

    force = lambda self: self.f

    __neg__ = lambda self: PointLoad(-self.f, self.p)
    
    __mul__ = lambda self, other: PointLoad(self.f * other, self.p)

    __repr__ = __str__ = lambda self: f"Pointload(Force={str(self.f)}, Point={str(self.p)})"
    
    __rmul__ = __mul__

class Moment:
    def __init__(self, value=[]):
        self.m = np.array(value)

    force, moment = lambda self: np.array([0, 0, 0]), lambda self: self.m

    momentx, momenty, momentz = [lambda self: self.moment()[i] for i in range(3)]

    __neg__ = lambda self: Moment(-self.m)
    __mul__, __add__ = lambda self, other: Moment(self.m * other), lambda self, other: Moment(self.m + other.m)
    __rmul__, __radd__ = __mul__, __add__
    __repr__ = __str__ = lambda self: f"Moment({self.m} Nm)"

class RunningLoad:
    def __init__(self, values=[], positions=[], axis=0, point=0):
        self.v, self.p, self.a = np.array(values), np.array(positions), axis
        self.z = point
        self.oa = list(range(3))
        self.oa.remove(axis)

    def force(self):
        forces = [quad(lambda x: np.interp(x, self.p, self.v[i, :]), self.p[0], self.p[-1])[0] for i in range(2)]
        f = list(range(3))
        f[self.a], (f[self.oa[0]], f[self.oa[1]]) = 0, forces
        return np.array(f)
    
    def moment(self):
        moi = [quad(lambda x: x * np.interp(x, self.p, self.v[i, :]), self.p[0], self.p[-1])[0] for i in range(2)]
        load = [quad(lambda x: np.interp(x, self.p, self.v[i, :]), self.p[0], self.p[-1])[0] for i in range(2)]
        poa = [moi[i] / load[i] for i in range(2)]
        poa1, poa2 = [0] * 3, [0] * 3
        load1, load2 = [0] * 3, [0] * 3
        poa1[self.a], poa2[self.a] = poa[0], poa[1]
        load1[self.oa[0]], load2[self.oa[1]] = load[0], load[1]
        l1, l2 = PointLoad(load1, poa1), PointLoad(load2, poa2)
        return l1.moment() + l2.moment()
    
    momentx, momenty, momentz = [lambda self: self.moment()[i] for i in range(3)]


class EquilibriumEquation:
    def __init__(self, kloads=[], ukloads=[]):
        self.k, self.uk = kloads, ukloads
        self.A, self.b = None, None

    def SetupEquation(self):
        b = np.concatenate([-sum([k.force() for k in self.k]), -sum([l.moment() for l in self.k])]).reshape(-1, 1)
        Forces = np.concatenate([l.force().reshape(-1, 1) for l in self.uk], axis=1)
        Moments = np.concatenate([l.moment().reshape(-1, 1) for l in self.uk], axis=1)
        
        sys = np.concatenate([(A := np.concatenate([Forces, Moments])).T, b.T]).T
        unsingularsys = sys[~np.all(sys == 0, axis=1)]
        self.A, self.b = unsingularsys[:, :-1], unsingularsys[:, -1]
        return self.A, self.b

    SolveEquation = lambda self: np.linalg.inv(self.A) @ self.b

if __name__ == '__main__':
    load1 = PointLoad([1, 0, 0], [0, 1, 0])
    load2 = PointLoad([1, 0, 0], [-1, 0, 0])
    load3 = PointLoad([0, 1, 0], [0, 1, 0])

    F1 = PointLoad([0, 1, 0], [0, 1, 0])
    F2 = PointLoad([1, 0, 0], [-1, 0, 0])
    F3 = PointLoad([0, -1, 0], [1, 0, 0])

    Eql = EquilibriumEquation(kloads=[load1, load2, load3], ukloads=[F1, F2, F3])
    Eql.SetupEquation()
    print(Eql.SolveEquation())
    print(F1 * Eql.SolveEquation()[0])
    q = RunningLoad([[1]*5, [2]*5], range(5), 0)
    print(q.force())
    print(q.moment())
