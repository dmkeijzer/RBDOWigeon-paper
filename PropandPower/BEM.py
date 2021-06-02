import numpy as np
import scipy.integrate as spint
import scipy.interpolate as spinplt
"""
This program calculates the blade geometry for propellers for minimum loss according to a procedure laid down by
ADKINS AND LIEBECK
"""


class BEM:
    def __init__(self, B, R, rpm, xi_0, rho, dyn_vis, V_fr, N_stations, a, RN_spacing, T=None, P=None):
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
        :param RN_spacing: Spacing of the Reynold's numbers of the airfoil data files [-] (added for flexibility,
                           but probably should be 100,000)

        :out: [0] -> speed ratio, used for iterations, internal variable
              [1] -> Array with relevant parameters for blade design and propeller performance:
                     [chord per station, beta per station, alpha per station, E per station, eff, Tc, Pc]
        """
        self.B = B
        self.R = R
        self.D = 2*R
        self.Omega = rpm * 2 * np.pi / 60  # rpm to rad/s
        self.xi_0 = xi_0
        self.rho = rho
        self.dyn_vis = dyn_vis
        self.V = V_fr
        self.phi_T = 1
        self.lamb = V_fr/(self.Omega*R)  # Speed ratio
        self.N_s = N_stations
        self.a = a
        self.RN_spacing = RN_spacing

        # Define thrust or power coefficients, depending on input
        if T is not None:
            self.Tc = 2 * T / (rho * V_fr**2 * np.pi * R**2)
            self.Pc = None
        elif P is not None:
            self.Pc = 2 * P / (rho * V_fr**3 * np.pi * R**2)
            self.Tc = None
        else:
            raise Exception("Please specify either T or P (not both)")

    # Prandtl relation for tip loss
    def F(self, xi, r, zeta):
        return (2/np.pi) * np.arccos(np.exp(-self.f(xi, r, zeta)))

    # Exponent used for function above
    def f(self, xi, r, zeta):
        return (self.B/2)*(1-xi(r))/(np.sin(self.phi_t(zeta)))

    # Pitch of blade tip
    def phi_t(self, zeta):
        return np.arctan(self.lamb * (1 + zeta/2))

    # Non-dimensional radius, r/R
    def Xi(self, r):
        return r/self.R

    # Angle of local velocity of the blade wrt to disk plane
    def phi(self, r, zeta):
        return np.arctan(np.tan(self.phi_t(zeta)) / self.Xi(r))

    # Mach as a function of radius
    def M(self, r):
        return self.Omega*r/self.a

    # Reynolds number
    def RN(self, Wc):
        # Reynolds number. Wc is speed times chord
        return Wc * self.rho / self.dyn_vis

    # def G(self):
    #     return F * np.cos(self.phi())

    # Product of local speed at the blade and chord
    def Wc(self, F, phi, zeta, Cl):
        return 4*np.pi*self.lamb * F * np.sin(phi) * np.cos(phi) * self.V * self.R * zeta / (Cl * self.B)

    # Non-dimensional speed
    def x(self, r):
        return self.Omega*r/self.V

    # # Integrals
    # def I_prim_1(self, xi, zeta, eps):
    #     return 4*xi*(2/np.pi)*np.arccos(np.exp(-self.B*(1-zeta)/(2*np.sin(self.phi_t(zeta))))) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
    #            (1 - eps*(1+zeta/2)*self.lamb/xi)
    #
    # def I_prim_2(self, xi, zeta, eps):
    #     return self.lamb*(4/np.pi)*np.arccos(np.exp(-self.B*(1-zeta)/(2*np.sin(self.phi_t(zeta))))) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
    #            (1 - eps*(1+zeta/2)*self.lamb/xi) * (1 + xi/((1+zeta/2)*self.lamb/xi)) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi))
    #
    # def J_prim_1(self, xi, zeta, eps):
    #     return 4*xi*(2/np.pi)*np.arccos(np.exp(-self.B*(1-zeta)/(2*np.sin(self.phi_t(zeta))))) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
    #            (1 + eps / ((1+zeta/2)*(self.lamb/xi)))
    #
    # def J_prim_2(self, xi, zeta, eps):
    #     return 2*xi*(2/np.pi)*np.arccos(np.exp(-self.B*(1-zeta)/(2*np.sin(self.phi_t(zeta))))) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi)) * np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
    #            (1 + eps / ((1+zeta/2)*(self.lamb/xi))) * (1 - eps*(1+zeta/2)*self.lamb/xi) * \
    #            (np.cos(np.arctan((1+zeta/2)*self.lamb/xi)))**2

    # Integrals used to calculate internal variables, refer to paper for more explanation if needed
    def I_prim_1(self, xi, zeta, eps):
        return 4 * xi * (2 / np.pi) * np.arccos(np.exp(-self.B * (1 - zeta) / (2 * np.sin(self.phi_t(zeta))))) * \
               np.cos(np.arctan((1 + zeta / 2) * self.lamb / xi)) * np.sin(np.arctan((1 + zeta/2) * self.lamb/xi)) * \
               (1 - eps(xi) * (1 + zeta / 2) * self.lamb / xi)

    def I_prim_2(self, xi, zeta, eps):
        return self.lamb * (4 / np.pi) * np.arccos(np.exp(-self.B * (1 - zeta) / (2 * np.sin(self.phi_t(zeta))))) * \
               np.cos(np.arctan((1 + zeta / 2) * self.lamb / xi)) * np.sin(
            np.arctan((1 + zeta / 2) * self.lamb / xi)) * \
               (1 - eps(xi) * (1 + zeta / 2) * self.lamb / xi) * (1 + xi / ((1 + zeta / 2) * self.lamb / xi)) * \
               np.cos(np.arctan((1 + zeta / 2) * self.lamb / xi)) * np.sin(
            np.arctan((1 + zeta / 2) * self.lamb / xi))

    def J_prim_1(self, xi, zeta, eps):
        return 4 * xi * (2 / np.pi) * np.arccos(np.exp(-self.B * (1 - zeta) / (2 * np.sin(self.phi_t(zeta))))) * \
               np.cos(np.arctan((1 + zeta / 2) * self.lamb / xi)) * np.sin(
            np.arctan((1 + zeta / 2) * self.lamb / xi)) * \
               (1 + eps(xi) / ((1 + zeta / 2) * (self.lamb / xi)))

    def J_prim_2(self, xi, zeta, eps):
        return 2 * xi * (2 / np.pi) * np.arccos(np.exp(-self.B * (1 - zeta) / (2 * np.sin(self.phi_t(zeta))))) * \
               np.cos(np.arctan((1 + zeta / 2) * self.lamb / xi)) * np.sin(
            np.arctan((1 + zeta / 2) * self.lamb / xi)) * \
               (1 + eps(xi) / ((1 + zeta / 2) * (self.lamb / xi))) * (1 - eps(xi) * (1 + zeta / 2) * self.lamb / xi) * \
               (np.cos(np.arctan((1 + zeta / 2) * self.lamb / xi))) ** 2

    # # Check convergence of the design procedure
    # # TODO: Check if current exception is an appropriate measure for convergence
    # def conv(self, zeta_new, zeta):
    #     try:
    #         return zeta_new/zeta
    #     except ZeroDivisionError:
    #         return zeta_new-zeta

    # Propeller efficiency Tc/Pc
    def efficiency(self, Tc, Pc):
        return Tc/Pc

    # Prandtl-Glauert correction factor
    def PG(self, M):
        return 1/np.sqrt(1 - M**2)

    # This function runs the design procedure from an arbitrary start zeta (which can be 0)
    def run_BEM(self, zeta):
        # Length of each station
        st_len = (self.R - self.R*self.xi_0)/self.N_s

        # Array with station numbers
        stations = np.arange(1, self.N_s + 1)

        # Radius of the middle point of each station
        stations_r = np.arange(st_len/2, self.R, st_len)

        # F and phi for each station
        F = self.F(self.Xi(stations_r), stations_r, zeta)
        phis = self.phi(stations_r, zeta)

        # TODO: Check if Cl range is good
        # Probably trial with a different range of Cls
        Cls_trial = np.arange(0.2, 1.1, 0.05)

        # Create arrays for lift and drag coefficients, angle of attack and D/L ratio for each station
        Cl = np.ones(self.N_s)
        Cd = np.ones(self.N_s)
        alpha = np.ones(self.N_s)
        E = np.ones(self.N_s)
        cs = np.ones(self.N_s)
        betas = np.ones(self.N_s)

        # Optimise each station for min D/L
        for station in stations:

            eps_min = 1
            optim_vals = [1, 1, 1, 1]

            # Optimise each station
            for lift_coef in Cls_trial:
                # TODO: Make this work for each station

                # Correct Cl with Prandtl-Glauert factor (using local Mach number in the middle of the station
                lift_coef = lift_coef * self.PG(self.M(stations_r[station]))

                # Calculate product of local speed with chord
                Wc = self.Wc(F[station], phis[station], zeta, lift_coef)

                # Calculate Reynolds number at the station to look for the correct airfoil datafile
                Reyn = self.RN(Wc)

                # Retrieve appropriate file from airfoil data folder
                RN = self.RN_spacing * round(Reyn[station] / self.RN_spacing)
                filename1 = "4412_Re{%d}_up" % RN
                filename2 = "4412_Re{%d}_dwn" % RN

                # TODO: implement open and read file code

                # TODO: See format of files and retrieve Cd and AoA from them
                Cd_ret = 1     # Retrieved Cd
                alpha_ret = 1  # Retrieved AoA

                # Compute D/L ration
                eps = Cd_ret / lift_coef

                # See if D/L is minimum. If so, save the values
                if eps < eps_min:
                    optim_vals = [lift_coef, Cd_ret, alpha_ret, eps, Wc]
                    eps_min = eps

            # Save the optimum config of the blade station
            Cl[station] = optim_vals[0]
            Cd[station] = optim_vals[1]
            alpha[station] = optim_vals[2]
            E[station] = optim_vals[3]

            local_Cl = optim_vals[0]
            local_Cd = optim_vals[1]
            local_AoA = optim_vals[2]
            local_eps = optim_vals[3]
            Wc = optim_vals[4]

            # Calculate interference factors
            a = (zeta/2) * (np.cos(phis[station]))**2 * (1 - local_eps*np.tan(phis[station]))
            a_prime = (zeta/(2*self.x(stations_r))) * np.cos(phis[station]) * np.sin(phis[station]) * \
                      (1 + local_eps/np.tan(phis[station]))

            # Calculate local speed at the blade station
            W = self.V * (1 + a) / np.sin(phis[station])

            # Calculate required chord of the station and save to array
            c = Wc/W
            cs[station] = c

            # Calculate blade pitch angle as AoA+phi and save to array
            beta = local_AoA + phis[station]
            betas[station] = beta

        # TODO: Is this local or general? Check current implementation
        # Possibly implement a function for eps as a function of r/R (xi)
        eps_fun = spinplt.interp1d(E, stations_r/self.R)

        # Integrate the derivatives from xi_0 to 1 (from hub to tip of the blade)
        I1 = spint.quad(self.I_prim_1, self.xi_0, 1, args=(zeta, eps_fun))[0]
        I2 = spint.quad(self.I_prim_2, self.xi_0, 1, args=(zeta, eps_fun))[0]
        J1 = spint.quad(self.J_prim_1, self.xi_0, 1, args=(zeta, eps_fun))[0]
        J2 = spint.quad(self.J_prim_2, self.xi_0, 1, args=(zeta, eps_fun))[0]

        # Calculate new speed ratio and Tc or Pc as required
        if self.Tc is not None:
            zeta_new = (I1/(2*I2)) - ((I1/(2*I2))**2 - self.Tc/I2)**(1/2)
            Pc = J1*zeta_new + J2*zeta_new**2

        elif self.Pc is not None:
            zeta_new = -(J1/(2*J2)) + ((J1/(2*J2))**2 + self.Pc/J2)**(1/2)
            Tc = I1*zeta_new - I2*zeta_new**2

        # Propeller efficiency
        eff = self.efficiency(Tc, Pc)

        return zeta_new, [cs, betas, alpha, E, eff, Tc, Pc]

    def optimise_blade(self, zeta_init):
        convergence = 1
        zeta = zeta_init
        # Optimisation converges for difference in zeta below 0.1%
        while convergence > 0.001:
            # Run BEM design procedure and retrieve new zeta
            design = self.run_BEM(zeta)
            zeta_new = design[0]

            # Check convergence
            try:
                convergence = zeta_new / zeta
            except ZeroDivisionError:
                convergence = zeta_new - zeta
            zeta = zeta_new

        return design

    # TODO
    # Implement a cycle with eps = 0 to calculate viscous losses

    # # Check convergence of the design procedure
    # # TODO: Check if current exception is an appropriate measure for convergence
    # def conv(self, zeta_new, zeta):
    #     try:
    #         return zeta_new/zeta
    #     except ZeroDivisionError:
    #         return zeta_new-zeta

    # Advance ratio
    def J(self):
        return self.V / ((self.Omega/(2*np.pi)) * self.D)

    def solidity(self):
        # TODO: implement solidity equation (based on page 46 of Veldhuis' thesis)
        return 1
