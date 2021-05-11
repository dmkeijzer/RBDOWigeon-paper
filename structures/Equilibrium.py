import numpy as np

class PointLoad:
    def __init__(self, force, point, known=True):
        self.p, self.k = point, known
        self.f = force / (np.linalg.norm(force) if not known else 1)
    
    moment = lambda self: np.cross(self.p, self.f)

    momentx, momenty, momentz = [lambda self: self.moment()[i] for i in range(3)]

    def __add__(self, other):
        return PointLoad(self.f + other.f, np.divide(self.p * self.f + other.p * other.f, self.f + other.f), self.k)
    
    def __neg__(self):
        return PointLoad(-self.f, self.p, self.k)
    
    def __str__(self):
        return f"Pointload(Force={str(self.f)}, Point={str(self.p)})"




class EquilibriumEquation:
    def __init__(self, kloads=[], ukloads=[]):
        self.k, self.uk = kloads, ukloads
        self.b = np.concatenate([-np.sum(kloads).f, -np.sum([l.moment() for l in kloads])])
        Forces = np.concatenate([l.f.reshape(-1, 1) for l in [F1, F2, F3]], axis=1)
        Moments = np.concatenate([l.moment().reshape(-1, 1) for l in [F1, F2, F3]], axis=1)
        self.A = np.concatenate([Forces, Moments])
    
if __name__ == '__main__':
    load1 = PointLoad(np.array([1, 0, 0]), np.array([0, 1, 0]))
    load2 = PointLoad(np.array([1, 0, 0]), np.array([-1, 0, 0]))
    load3 = PointLoad(np.array([0, 1, 0]), np.array([0, 1, 0]))

    F1 = PointLoad(np.array([0, 1, 0]), np.array([0, 1, 0]), False)
    F2 = PointLoad(np.array([1, 0, 0]), np.array([-1, 0, 0]), False)
    F3 = PointLoad(np.array([0, -1, 0]), np.array([1, 0, 0]), False)

    Eql = EquilibriumEquation(kloads=[load1, load2, load3], ukloads=[F1, F2, F3])
    print(Eql.b, '\n', Eql.A)
    # Forces = np.concatenate([l.f.reshape(-1, 1) for l in [F1, F2, F3]], axis=1)
    # Moments = np.concatenate([l.moment().reshape(-1, 1) for l in [F1, F2, F3]], axis=1)
    # print(np.concatenate([Forces, Moments]))