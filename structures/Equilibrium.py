import numpy as np

class PointLoad:
    def __init__(self, force, point, known=True):
        self.p, self.k = np.array(point), known
        self.f = np.array(force) / (np.linalg.norm(force) if not known else 1)

    moment = lambda self: np.cross(self.p, self.f)

    momentx, momenty, momentz = [lambda self: self.moment()[i] for i in range(3)]

    force = lambda self: self.f

    def __add__(self, other):
        return PointLoad(self.f + other.f, np.divide(self.p * self.f + other.p * other.f, self.f + other.f), self.k)

    def __neg__(self):
        return PointLoad(-self.f, self.p, self.k)

    def __str__(self):
        return f"Pointload(Force={str(self.f)}, Point={str(self.p)})"

class Moment:
    def __init__(self, value=[]):
        self.m = np.array(value)

    force, moment = lambda self: np.array([0, 0, 0]), lambda self: self.m

class RunningLoad:
    def __init__(self, values=[], positions=[], axis=0):

class EquilibriumEquation:
    def __init__(self, kloads=[], ukloads=[]):
        self.k, self.uk = kloads, ukloads
        self.A, self.b = None, None
    
    def SetupEquation(self):
        b = np.concatenate([-np.sum(self.k).force(), -sum([l.moment() for l in self.k])]).reshape(-1, 1)
        Forces = np.concatenate([l.force().reshape(-1, 1) for l in self.uk], axis=1)
        Moments = np.concatenate([l.moment().reshape(-1, 1) for l in self.uk], axis=1)
        
        sys = np.concatenate([(A := np.concatenate([Forces, Moments])).T, b.T]).T
        unsingularsys = sys[~np.all(sys == 0, axis=1)]
        self.A, self.b = unsingularsys[:, :-1], unsingularsys[:, -1]
        return self.A, self.b

    SolveEquation = lambda self: np.linalg.inv(self.A) @ self.b
    
if __name__ == '__main__':
    load1 = PointLoad(np.array([1, 0, 0]), np.array([0, 1, 0]))
    load2 = PointLoad(np.array([1, 0, 0]), np.array([-1, 0, 0]))
    load3 = PointLoad(np.array([0, 1, 0]), np.array([0, 1, 0]))

    F1 = PointLoad(np.array([0, 1, 0]), np.array([0, 1, 0]), False)
    F2 = PointLoad(np.array([1, 0, 0]), np.array([-1, 0, 0]), False)
    F3 = PointLoad(np.array([0, -1, 0]), np.array([1, 0, 0]), False)

    Eql = EquilibriumEquation(kloads=[load1, load2, load3], ukloads=[F1, F2, F3])
    Eql.SetupEquation()
    print(Eql.SolveEquation())