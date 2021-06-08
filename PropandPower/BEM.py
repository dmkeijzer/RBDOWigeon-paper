import numpy as np
import scipy.integrate as spint
import scipy.interpolate as spinplt
"""
This program calculates the blade geometry for propellers with minimum loss according to a procedure laid down by
ADKINS AND LIEBECK, based on Larrabee.
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
    def F(self, r, zeta):
        return (2/np.pi) * np.arccos(np.exp(-self.f(r, zeta)))

    # Exponent used for function above
    def f(self, r, zeta):
        return (self.B/2)*(1-self.Xi(r))/(np.sin(self.phi_t(zeta)))

    # Pitch of blade tip
    def phi_t(self, zeta):
        return np.arctan(self.lamb * (1 + zeta/2))

    # Non-dimensional radius, r/R
    def Xi(self, r):
        return r/self.R

    # Angle of local velocity of the blade wrt to disk plane
    def phi(self, r, zeta):
        return np.arctan(np.tan(self.phi_t(zeta)) * self.R / r)

    # Mach as a function of radius
    def M(self, r):
        return self.Omega*r/self.a

    # Reynolds number
    def RN(self, Wc):
        # Reynolds number. Wc is speed times chord
        return Wc * self.rho / self.dyn_vis

    # Product of local speed at the blade and chord
    def Wc(self, F, phi, zeta, Cl):
        # print(self.lamb)
        # print(F)
        # print(np.sin(phi))
        # print(np.cos(phi))
        # print(self.V)
        # print(self.R)
        # print(zeta)
        # print(Cl)
        # print(self.B)
        # print("")
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

    def phi_int(self, xi, zeta):
        return np.arctan((1 + zeta/2)*self.lamb/xi)

    # F function used for integration part only
    def F_int(self, xi, zeta):
        return 2*np.arccos(np.exp(-self.f_int(xi, zeta)))/np.pi

    # f function used for integration part only
    def f_int(self, xi, zeta):
        return (self.B/2)*(1 - xi)/np.sin(self.phi_t(zeta))

    # G function used for integration part only
    def G_int(self, xi, zeta):
        return self.F_int(xi, zeta) * np.cos(self.phi_t(zeta)) * np.sin(self.phi_t(zeta))

    # # Integrals used to calculate internal variables, refer to paper for more explanation if needed
    # def I_prim_1(self, xi, zeta, eps):
    #     return 4 * xi * self.G_int(xi, zeta) * (1 - eps(xi)*np.tan(self.phi_int(xi, zeta)))
    #
    # def I_prim_2(self, xi, zeta, eps):
    #     return self.lamb * (self.I_prim_1(xi, zeta, eps)/(2*xi)) * (1 + eps(xi)/np.tan(self.phi_int(xi, zeta))) * \
    #            np.sin(self.phi_int(xi, zeta)) * np.cos(self.phi_int(xi, zeta))
    #
    # def J_prim_1(self, xi, zeta, eps):
    #     return 4 * xi * self.G_int(xi, zeta) * (1 + eps(xi) / np.tan(self.phi_int(xi, zeta)))
    #
    # def J_prim_2(self, xi, zeta, eps):
    #     return (self.J_prim_1(xi, zeta, eps)/2) * (1 - eps(xi)*np.tan(self.phi_int(xi, zeta))) * \
    #            (np.cos(self.phi_int(xi, zeta)))**2

    # Integrals used to calculate internal variables, refer to paper for more explanation if needed
    # Assuming average eps
    def I_prim_1(self, xi, zeta, eps):
        return 4 * xi * self.G_int(xi, zeta) * (1 - eps * np.tan(self.phi_int(xi, zeta)))

    def I_prim_2(self, xi, zeta, eps):
        return self.lamb * (self.I_prim_1(xi, zeta, eps) / (2 * xi)) * (1 + eps / np.tan(self.phi_int(xi, zeta))) * \
               np.sin(self.phi_int(xi, zeta)) * np.cos(self.phi_int(xi, zeta))

    def J_prim_1(self, xi, zeta, eps):
        return 4 * xi * self.G_int(xi, zeta) * (1 + eps / np.tan(self.phi_int(xi, zeta)))

    def J_prim_2(self, xi, zeta, eps):
        return (self.J_prim_1(xi, zeta, eps) / 2) * (1 - eps * np.tan(self.phi_int(xi, zeta))) * \
               (np.cos(self.phi_int(xi, zeta))) ** 2

    # # Integrals used to calculate internal variables, refer to paper for more explanation if needed
    # # Assuming average eps
    # def I_prim_1(self, xi, zeta, eps):
    #     return 4*xi*(2/np.pi)*np.arccos(np.exp(-self.B*np.sin(self.phi_t(zeta))*(1-xi)/2)) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi))*np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
    #            (1 - eps*(1+zeta/2)*self.lamb/xi)
    #
    # def I_prim_2(self, xi, zeta, eps):
    #     return 2*self.lamb * (2/np.pi)*np.arccos(np.exp(-self.B*np.sin(self.phi_t(zeta))*(1-xi)/2)) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi))*np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
    #            (1 - eps*(1+zeta/2)*self.lamb/xi) * (1 + eps/((1+zeta/2)*self.lamb/xi)) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi))*np.sin(np.arctan((1+zeta/2)*self.lamb/xi))
    #
    # def J_prim_1(self, xi, zeta, eps):
    #     return 4*xi*(2/np.pi)*np.arccos(np.exp(-self.B*np.sin(self.phi_t(zeta))*(1-xi)/2)) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi))*np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
    #            (1 + eps / ((1+zeta/2) * self.lamb / xi))
    #
    # def J_prim_2(self, xi, zeta, eps):
    #     return 2*xi*(2/np.pi)*np.arccos(np.exp(-self.B*np.sin(self.phi_t(zeta))*(1-xi)/2)) * \
    #            np.cos(np.arctan((1+zeta/2)*self.lamb/xi))*np.sin(np.arctan((1+zeta/2)*self.lamb/xi)) * \
    #            (1 + eps / ((1+zeta/2) * self.lamb / xi)) * (1 - eps*(1+zeta/2)*self.lamb/xi) * \
    #            (np.cos(np.arctan((1+zeta/2)*self.lamb/xi)))**2

    # # Integrals used to calculate internal variables, refer to paper for more explanation if needed
    # def I_prim_1(self, xi, zeta, eps):
    #     return 4 * xi * (2 / np.pi) * np.arccos(np.exp(-self.B * (1 - xi) / (2 * np.sin(self.phi_t(zeta))))) * \
    #            np.cos(np.arctan((1 + zeta / 2) * self.lamb / xi)) * np.sin(np.arctan((1 + zeta/2) * self.lamb/xi)) * \
    #            (1 - eps(xi) * (1 + zeta / 2) * self.lamb / xi)
    #
    # def I_prim_2(self, xi, zeta, eps):
    #     return self.lamb * (4 / np.pi) * np.arccos(np.exp(-self.B * (1 - xi) / (2 * np.sin(self.phi_t(zeta))))) * \
    #            np.cos(np.arctan((1 + zeta/2) * self.lamb / xi)) * np.sin(np.arctan((1 + zeta / 2) * self.lamb/xi)) * \
    #            (1 - eps(xi) * (1 + zeta / 2) * self.lamb / xi) * (1 + xi / ((1 + zeta / 2) * self.lamb / xi)) * \
    #            np.cos(np.arctan((1 + zeta/2) * self.lamb/xi)) * np.sin(np.arctan((1 + zeta/2) * self.lamb / xi))
    #
    # def J_prim_1(self, xi, zeta, eps):
    #     return 4 * xi * (2 / np.pi) * np.arccos(np.exp(-self.B * (1 - xi) / (2 * np.sin(self.phi_t(zeta))))) * \
    #            np.cos(np.arctan((1 + zeta/2) * self.lamb / xi)) * np.sin(np.arctan((1 + zeta/2) * self.lamb / xi)) * \
    #            (1 + eps(xi) / ((1 + zeta / 2) * (self.lamb / xi)))
    #
    # def J_prim_2(self, xi, zeta, eps):
    #     return 2 * xi * (2 / np.pi) * np.arccos(np.exp(-self.B * (1 - xi) / (2 * np.sin(self.phi_t(zeta))))) * \
    #            np.cos(np.arctan((1 + zeta/2) * self.lamb/xi)) * np.sin(np.arctan((1 + zeta / 2) * self.lamb / xi)) * \
    #            (1 + eps(xi) / ((1 + zeta / 2) * (self.lamb/xi))) * (1 - eps(xi) * (1 + zeta / 2) * self.lamb / xi) * \
    #            (np.cos(np.arctan((1 + zeta / 2) * self.lamb / xi))) ** 2

    # Propeller efficiency Tc/Pc
    def efficiency(self, Tc, Pc):
        return Tc/Pc

    # Prandtl-Glauert correction factor: sqrt(1 - M^2)
    def PG(self, M):
        return np.sqrt(1 - M**2)

    # This function runs the design procedure from an arbitrary start zeta (which can be 0)
    def run_BEM(self, zeta):
        # Array with station numbers
        stations = np.arange(1, self.N_s + 1)

        # Length of each station
        st_len = (self.R - self.R*self.xi_0)/len(stations)

        # Radius of the middle point of each station.
        # Station 1 has st length/2, each station has that plus N*st length
        # Station 1 starts after hub
        stations_r = self.xi_0*self.R + st_len/2 + (stations-1)*st_len

        # F and phi for each station
        # self.Xi(stations_r),
        F = self.F(stations_r, zeta)
        phis = self.phi(stations_r, zeta)

        # TODO: Check if Cl range is good
        # Probably trial with a different range of Cls
        Cls_trial = np.arange(0.1, 1, 0.05)

        # Create arrays for lift and drag coefficients, angle of attack and D/L ratio for each station
        Cl = np.ones(self.N_s)
        Cd = np.ones(self.N_s)
        alpha = np.ones(self.N_s)
        E = np.ones(self.N_s)
        cs = np.ones(self.N_s)
        betas = np.ones(self.N_s)

        # Optimise each station for min D/L
        for station in stations:
            station -= 1
            eps_min = 1
            optim_vals = [1, 1, 1, 1]

            # Optimise each station
            for lift_coef in Cls_trial:
                # lift_coef = lift_coef * self.PG(self.M(stations_r[station]))

                # Calculate product of local speed with chord
                Wc = self.Wc(F[station], phis[station], zeta, lift_coef)

                # Calculate Reynolds number at the station to look for the correct airfoil datafile
                Reyn = self.RN(Wc)

                # Round Reynolds number to 100,000 to retrieve appropriate file from airfoil data folder
                RN = self.RN_spacing * round(Reyn / self.RN_spacing)

                # Maximum and minimum RN in database
                if RN<100000:
                    RN = 100000
                if RN>5000000:
                    RN = 5000000

                # Look for corresponding airfoil data file for that RN
                filename1 = "4412_Re%d_up.txt" % RN
                filename2 = "4412_Re%d_dwn.txt" % RN

                file_up = open('Airfoil_Data/'+filename1, "r")
                file_down = open('Airfoil_Data/'+filename2, "r")

                # Read lines
                lines_up = file_up.readlines()
                lines_down = file_up.readlines()

                # Close files
                file_up.close()
                file_down.close()

                # List and Boolean to save relevant lines
                format_lines = []
                save_lines = False

                for line in lines_up:
                    # Separate variables inside file
                    a = line.split()

                    # If the save_lines boolean is True (when the code gets to numerical values), save to list
                    if save_lines:
                        # Create a line with floats (instead of strings) to append to main list
                        new_line = []
                        for value in a:
                            new_line.append(float(value))
                        format_lines.append(new_line)

                    # Protect against empty lines
                    if len(a) > 0:
                        # There is a line with ---- before the numbers, so once we get to this line, start saving
                        if a[0].count('-') >= 1:
                            save_lines = True

                # Restart boolean for down file
                save_lines = False

                # Do the same process for down file and append to the same array as up
                for line in lines_down:
                    a = line.split()

                    if save_lines:
                        new_line = []
                        for value in a:
                            new_line.append(float(value))
                        format_lines.append(new_line)

                    if len(a) > 0:
                        if a[0].count('-') >= 1:
                            save_lines = True

                # Convert to numpy array with airfoil data
                airfoil_data = np.array(format_lines)

                # Format of each line:
                # alpha, CL, CD, Re(CL), CM, S_xtr, P_xtr, CDp

                # Order airfoil data by angle of attack, this can be eliminated to save time if needed
                airfoil_data = airfoil_data[airfoil_data[:, 0].argsort()]

                # Get index of line where Cl is the closest to the used value

                # Save airfoil data array to have a copy to modify
                airfoil_data_check = airfoil_data

                # Subtract current Cl from list of Cls
                # 'Uncorrect' Cl for Mach, since the files do not take Mach into account, only RN
                # TODO: revise Mach corrections, maybe use W
                airfoil_data_check[:, 1] -= (lift_coef * self.PG(self.M(stations_r[station])))

                # Check what line has min Cl difference, and retrieve index of that column
                index = np.argmin(np.abs(airfoil_data_check[:, 1]))

                # Obtain the Cd and AoA from the line where Cl difference is min
                Cd_ret = airfoil_data[index, 2]                   # Retrieved Cd
                alpha_ret = np.deg2rad(airfoil_data[index, 0])    # Retrieved AoA convert from deg to rad

                # Compute D/L ration
                eps = Cd_ret / lift_coef

                # See if D/L is minimum. If so, save the values
                if eps < eps_min and airfoil_data[index, 1] > 0:
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

        # # Possibly implement a function for eps as a function of r/R (xi)
        # eps_fun = spinplt.interp1d(E, stations_r/self.R, fill_value="extrapolate")
        #
        # # Integrate the derivatives from xi_0 to 1 (from hub to tip of the blade)
        # I1 = spint.quad(self.I_prim_1, self.xi_0, 1, args=(zeta, eps_fun))[0]
        # I2 = spint.quad(self.I_prim_2, self.xi_0, 1, args=(zeta, eps_fun))[0]
        # J1 = spint.quad(self.J_prim_1, self.xi_0, 1, args=(zeta, eps_fun))[0]
        # J2 = spint.quad(self.J_prim_2, self.xi_0, 1, args=(zeta, eps_fun))[0]

        # Use average epsilon, independent of r/R (xi), to simplify calculations, as it is very similar in all stations
        eps_avg = np.average(E)

        # Integrate the derivatives from xi_0 to 1 (from hub to tip of the blade)
        I1 = spint.quad(self.I_prim_1, self.xi_0, 1, args=(zeta, eps_avg))[0]
        I2 = spint.quad(self.I_prim_2, self.xi_0, 1, args=(zeta, eps_avg))[0]
        J1 = spint.quad(self.J_prim_1, self.xi_0, 1, args=(zeta, eps_avg))[0]
        J2 = spint.quad(self.J_prim_2, self.xi_0, 1, args=(zeta, eps_avg))[0]

        # print("I1:", I1)
        # print("I2:", I2)
        # print("J1:", J1)
        # print("J2:", J2)
        # print("")

        # Calculate new speed ratio and Tc or Pc as required
        if self.Tc is not None:
            zeta_new = (I1/(2*I2)) - ((I1/(2*I2))**2 - self.Tc/I2)**(1/2)
            Pc = J1*zeta_new + J2*zeta_new**2

            # Propeller efficiency
            eff = self.efficiency(self.Tc, Pc)

            return zeta_new, [cs, betas, alpha, stations_r, E, eff, self.Tc, Pc]

        elif self.Pc is not None:
            zeta_new = -(J1/(2*J2)) + ((J1/(2*J2))**2 + self.Pc/J2)**(1/2)
            Tc = I1*zeta_new - I2*zeta_new**2

            # Propeller efficiency
            eff = self.efficiency(Tc, self.Pc)

            return zeta_new, [cs, betas, alpha, stations_r, E, eff, Tc, self.Pc]

    def optimise_blade(self, zeta_init):
        convergence = 1
        zeta = zeta_init
        # Optimisation converges for difference in zeta below 0.1%
        while convergence > 0.001:
            # Run BEM design procedure and retrieve new zeta
            design = self.run_BEM(zeta)
            zeta_new = design[0]

            # Check convergence
            if zeta == 0:
                convergence = zeta_new - zeta
            else:
                convergence = np.abs(zeta_new - zeta)/zeta

            zeta = zeta_new
        #     print(convergence, "conv")
        #
        # print("Zeta:", zeta)
        design = self.run_BEM(zeta)
        return design

    # TODO
    # Implement a cycle with eps = 0 to calculate viscous losses

    # Advance ratio
    def J(self):
        return self.V / ((self.Omega/(2*np.pi)) * self.D)

    def solidity(self):
        # TODO: implement solidity equation (based on page 46 of Veldhuis' thesis)
        return 1
