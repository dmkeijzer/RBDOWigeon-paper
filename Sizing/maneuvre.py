import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def maneuvrenv(V, Vs, WoS, CLmax, pos=True):
    n = lambda CL, V, WoS: 0.5 * rho(avg_alt) * V ** 2 * CL / WoS
    nmin, nmax = -1, 2.5 # UAM reader
    Vc, VD = Vs
    interpolate = lambda V, V1, V2, n1, n2: n1 + (V - V1) * (n2 - n1) / (V2 - V1)
    return min(n(CLmax, V, WoS), nmax) if pos else \
    ( max(-n(CLmax, V, WoS), nmin) if V <= Vc else interpolate(V, Vc, VD, nmin, 0))

def plotmaneuvrenv(WoS, Vc, CLmax):
    VD = design_dive_speed(Vc)
    Vs = Vc, VD
    x = np.linspace(0, VD, 100)
    ax = sns.lineplot(x=x, y=[maneuvrenv(V, Vs, WoS, CLmax, True) for V in x], color='red')
    sns.lineplot(x=x, y=[maneuvrenv(V, Vs, WoS, CLmax, False) for V in x], color='red', label='Maneuvre Envelope')
    ax.set(xlabel="V [m/s]", ylabel="n [-]")
    plt.plot([VD, VD], [maneuvrenv(VD, Vs, WoS, CLmax, False), maneuvrenv(VD, Vs, WoS, CLmax, True)], color='red')
    # plt.savefig('maneuvre.png')
