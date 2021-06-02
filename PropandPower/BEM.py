import numpy as np
import scipy.integrate as spint
"""
This program calculates the blade geometry for propellers for minimum loss according to a procedure laid down by
ADKINS AND LIEBECK
"""


class BEM:
    def __init__(self, B, R, rpm, xi_0, rho, dyn_vis, V_fr, N_stations, a, T=None, P=None):
        """
        :param B: Number of blades [-]
        :param R: Outer radius of propeller [m]
        :param rpm: rpm of the propeller [rpm]
        :param xi_0: Non-dimensional hub radius (r_hub/R) [-]
        :param rho: Density [kg/m^3]
        :param dyn_vis: Dynamic viscosity [N s/m^2)
        :param V_fr: Freestream velocity
        :param T: Thrust delivered BY the propeller [N]
        :param P: Power delivered TO the propeller [W]
        :param N_stations: Number of stations to calculate [-]
        :param a: Speed of sound [m/s]
        """
        self.B = B
        self.R = R
        self.Omega = rpm * 2 * np.pi / 60  # rpm to rad/s
        self.xi_0 = xi_0
        self.rho = rho
        self.dyn_vis = dyn_vis
        self.V = V_fr
        self.phi_T = 1
        self.lamb = V_fr/(self.Omega*R)  # Speed ratio
        self.N_s = N_stations
        self.a = a
        if T is not None:
            self.Tc = 2 * T / (rho * V_fr**2 * np.pi * R**2)
            self.Pc = None

        elif P is not None:
            self.Pc = 2 * P / (rho * V_fr**3 * np.pi * R**2)
            self.Tc = None

    # Prandtl relation for tip loss
    def F(self, xi, r, zeta):
        return (2/np.pi) * np.arccos(np.exp(-self.f(xi, r, zeta)))

    def f(self, xi, r, zeta):
        return (self.B/2)*(1-xi(r))/(np.sin(self.phi_t(zeta)))

    # Pitch of blade tip
    def phi_t(self, zeta):
        return np.arctan(self.lamb * (1 + zeta/2))

    def xi(self, r):
        return r/self.R

    def phi(self, r, zeta):
        return np.arctan(np.tan(self.phi_t(zeta)) / self.xi(r))

    def M(self, r):
        return self.Omega*r/self.a

    def RN(self, Wc):
        # Reynolds number. Wc is speed times chord
        return Wc * self.rho / self.dyn_vis

    # def G(self):
    #     return F * np.cos(self.phi())

    # Product of W speed and chord
    def Wc(self, F, phi, zeta, Cl):
        return 4*np.pi*self.lamb * F * np.sin(phi) * np.cos(phi) * self.V * self.R * zeta / (Cl * self.B)

    # Non-dimensional speed
    def x(self, r):
        return self.Omega*r/self.V

    # Integrals
    def I_prim_1(self, xi, zeta, eps):
        return 4*xi*(2/np.pi)*np.arccos(np.exp(-self.B*(1-zeta)/(2*np.sin(self.phi_t(zeta))))) * \
               np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
               (1 - eps*(1+zeta/2)*self.lamb/xi)

    def I_prim_2(self, xi, zeta, eps):
        return self.lamb*(4/np.pi)*np.arccos(np.exp(-self.B*(1-zeta)/(2*np.sin(self.phi_t(zeta))))) * \
               np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
               (1 - eps*(1+zeta/2)*self.lamb/xi) * (1 + xi/((1+zeta/2)*self.lamb/xi)) * \
               np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi))

    def J_prim_1(self, xi, zeta, eps):
        return 4*xi*(2/np.pi)*np.arccos(np.exp(-self.B*(1-zeta)/(2*np.sin(self.phi_t(zeta))))) * \
               np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
               (1 + eps / ((1+zeta/2)*(self.lamb/xi)))

    def J_prim_2(self, xi, zeta, eps):
        return 2*xi*(2/np.pi)*np.arccos(np.exp(-self.B*(1-zeta)/(2*np.sin(self.phi_t(zeta))))) * \
               np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
               (1 + eps / ((1+zeta/2)*(self.lamb/xi))) * (1 - eps*(1+zeta/2)*self.lamb/xi) * \
               (np.cos(np.arctan((1+zeta/2)*self.lamb/xi)))**2

    def conv(self, zeta_new, zeta):
        try:
            return zeta_new/zeta
        except ZeroDivisionError:
            return 0

    def efficiency(self, Tc, Pc):
        return Tc/Pc

    # This function runs the design procedure from an arbitrary start zeta (which can be 0)
    def run_BEM(self, zeta):
        st_len = (self.R - self.R*self.xi_0)/self.N_s
        stations_r = np.arange(st_len/2, self.R, st_len)
        F = self.F(self.xi(stations_r), stations_r, zeta)
        phis = self.phi(stations_r, zeta)

        Wc = self.Wc(F, phis, zeta)
        Reyn = self.RN(Wc)

        # TODO
        # Get epsilon (D/L) and AoA from airfoil data
        eps = 1
        alpha = 1
        # Optimise eps and recalculated Wc and eps and alpha

        a = (zeta/2) * (np.cos(phis))**2 * (1 - eps*np.tan(phis))
        a_prime = (zeta/(2*self.x(stations_r))) * np.cos(phis) * np.sin(phis) * (1 + eps/np.tan(phis))

        W = self.V * (1 + a) / np.sin(phis)

        c = Wc/W

        # Blade angle is AoA+phi
        beta = alpha + phis

        # Integrate the derivatives from xi_0 to 1 (from hub to tip of the blade)
        I1 = spint.quad(self.I_prim_1, self.xi_0, 1, args=(zeta, eps))[0]
        I2 = spint.quad(self.I_prim_2, self.xi_0, 1, args=(zeta, eps))[0]
        J1 = spint.quad(self.J_prim_1, self.xi_0, 1, args=(zeta, eps))[0]
        J2 = spint.quad(self.J_prim_2, self.xi_0, 1, args=(zeta, eps))[0]

        # Calculate
        if self.Tc is not None:
            zeta_new = (I1/(2*I2)) - ((I1/(2*I2))**2 - self.Tc/I2)**(1/2)
            Pc = J1*zeta_new + J2*zeta_new**2

        elif self.Pc is not None:
            zeta_new = -(J1/(2*J2)) + ((J1/(2*J2))**2 + self.Pc/J2)**(1/2)
            Tc = I1*zeta_new - I2*zeta_new**2

        eff = self.efficiency(Tc, Pc)

        return zeta_new

    def optimise_blade(self, zeta):
        zeta_new = 1
        convergence = 1
        while convergence > 0.001:
            zeta_new = self.run_BEM(zeta)
            convergence = self.conv(zeta_new, zeta)
        return zeta_new

    def solidity(self):
        # TODO
        return 1
