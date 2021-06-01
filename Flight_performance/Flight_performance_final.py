import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from Aero_tools import ISA


class mission:
    def __init__(self):

        self.h_cruise = 300
        self.a = 2 * np.pi
        self.mission_dist = 300e8
        self.S = 10

        self.g = 9.80665

        self.m = 2000

        self.ax_target = 0.5*self.g
        self.ay_target = 0.1*self.g

    def aero_coefficients(self, angle_of_attack):
        """
        Calculates the lift and drag coefficients of the aircraft for a given angle of attack.
        This function will be implemented when the format of the aerodynamic analysis done by the aerodynamic department
        is known.

        :param angle_of_attack: angle of attack experienced by the wing [rad]
        :return: CL and CD
        """

        # Placeholder values for the lift and drag coefficients

        if angle_of_attack<np.radians(20):
            CL = angle_of_attack * 2 * np.pi

        else:
            CL = np.maximum(np.radians(15)* 2 * np.pi - (2*(angle_of_attack - np.radians(20))), 0)

        CD = 0.05 + 0.05 * ((angle_of_attack * 2 * np.pi)**2)

        return CL, CD

    def thrust_to_power(self, T, V):
        """
        This function calculates the available power associated with a certain thrust level. Note that this power
        still needs to be converted to brake power later on. This will be implemented when more is known about this
        from the power and propulsion department

        :param T: Thrust provided by the engines [N]
        :param V: Airspeed [m/s]
        :return: P_a: available power
        """

        P_a = 1e6

        return P_a

    def system(self, p, D, gamma, L, ax_tgt, ay_tgt):

        T, th = p

        return ((-D*np.cos(gamma) - L*np.sin(gamma) + T*np.cos(th)) -self.m*ax_tgt,
                (L*np.cos(gamma) - self.m*self.g - D*np.sin(gamma) + T*np.sin(th)) - self.m*ay_tgt)

    def target_accelerations(self, vx, vy):

        # Re-set the target values, such that the conditions below have to be re-evaluated each time
        ay_tgt = self.ay_target
        ax_tgt = self.ax_target

        # Distance needed to slow down the rate of climb
        d_rc = vy / ay_tgt

        # Check if target values have been reached
        if np.abs(vx - vx_tgt) < 5:
            ax_tgt = -0.5 * (vx - vx_tgt)

        # Do not start transition when altitude< 10 m for safety
        if y < 10:
            ax_tgt = 0

        if vy >= rc_tgt:
            ay_tgt = 0

        # Start reducing the R/C when approaching the cruising altitude
        if y >= h_tgt - d_rc:
            ay_tgt = -self.ay_target

            # If within 5 meters of the target altitude,
            # change to a proportional-differential control of acceleration,
            # for smooth arrival and passenger comfort
            if np.abs(y - h_tgt) < 10:
                ay_tgt = -0.05 * (y - h_tgt) - 0.5 * vy

        return ax_tgt, ay_tgt

    def numerical_simulation(self):#, init_vals, target_vals):

        # Just to avoid errors, remove when implementing things
        alpha = 0
        V = 0
        T = 0
        distance = 0
        energy = 0
        time = 0

        # Initialization
        vx = 0.001#init_vals['vx']  # [m/s] Speed in x-direction
        vy = 0#init_vals['vy']  # [m/s] Speed in y-direction, small value to prevent divide by zero
        climb = True #init_vals['climb']  # [bool] True if climbing, false if descending
        t = 0
        x = 0
        y = 0#init_vals['h_start']
        th = np.pi/2
        max_rot = 4*np.pi/180
        dt = 0.01

        # Target values
        h_tgt = 300# target_vals['h_target']
        vx_tgt = 60#target_vals['vx_target']
        vy_tgt = 0#target_vals['vy_target']
        rc_tgt = 5
        ax_tgt = self.ax_target#0.3*self.g
        ay_tgt = self.ay_target#0.3*self.g

        # Lists to store everything
        y_lst = []
        x_lst = []
        vy_lst = []
        vx_lst = []
        th_lst = []
        T_lst = []
        t_lst = []
        ax_lst = []
        ay_lst = []

        # Preliminary calculations
        running = True
        while running:

            t += dt

            # ======== Actual Simulation ========

            rho = ISA(y).density()
            V = np.sqrt(vx ** 2 + vy ** 2)
            gamma = np.arctan(vy / vx)
            alpha = th - gamma

            # Get the aerodynamic coefficients
            CL, CD = self.aero_coefficients(alpha)

            # Make aerodynamic forces dimensional
            L = 0.5 * rho * V * V * self.S * CL
            D = 0.5 * rho * V * V * self.S * CD

            # Re-set the target values, such that the conditions below have to be re-evaluated each time
            ay_tgt = self.ay_target
            ax_tgt = self.ax_target

            # Distance needed to slow down the rate of climb
            d_rc = vy/ay_tgt

            # Check if target values have been reached
            if np.abs(vx - vx_tgt) < 5:
                ax_tgt = -0.5*(vx-vx_tgt)

            # Do not start transition when altitude< 10 m for safety
            if y<10:
                ax_tgt = 0

            if vy >= rc_tgt:
                ay_tgt = 0

            # Start reducing the R/C when approaching the cruising altitude
            if y >= h_tgt-d_rc:
                ay_tgt = -self.ay_target

                # If within 5 meters of the target altitude,
                # change to a proportional-differential control of acceleration,
                # for smooth arrival and passenger comfort
                if np.abs(y - h_tgt) < 10:
                    ay_tgt = -0.05*(y-h_tgt) - 0.5*vy

            ax_tgt, ay_tgt = self.target_accelerations()

            # If a constraint on rotational speed is added, calculate the limits in rotation
            th_min, th_max  = th - max_rot*dt, th + max_rot*dt
            T_min, T_max    = T - 200, T + 200

            # Calculate the accelerations
            ax = (-D*np.cos(gamma) - L*np.sin(gamma) + T*np.cos(th))/self.m
            ay = (L*np.cos(gamma) - self.m*self.g - D*np.sin(gamma) + T*np.sin(th))/self.m

            # Solve for the thrust and wing angle, using the target acceleration values
            th = np.arctan2((self.m * ay_tgt + self.m * self.g - L * np.cos(gamma) + D * np.sin(gamma)),
                           (self.m * ax_tgt + D * np.cos(gamma) + L * np.sin(gamma)))

            th = np.maximum(np.minimum(th, th_max), th_min)

            # Thrust can be calculated in two ways, result should be very close
            T  = (self.m * ax_tgt + D * np.cos(gamma) + L * np.sin(gamma))/np.cos(th)
            T  = (self.m*ay_tgt + self.m*self.g - L*np.cos(gamma) + D*np.sin(gamma))/np.sin(th)

            T = np.maximum(np.minimum(np.maximum(T, T_min), T_max), 0)

            #print('accelerations:', ax - ax_tgt, ay - ay_tgt)
            #print('forces:', CL, CD, D)

            # Perform numerical integration
            vx  += ax*dt
            vy  += ay*dt

            x   += vx*dt
            y   += vy*dt

            # Prevent going underground
            y   = np.maximum(y, 0)

            # ======= Get Required outputs =======

            # Get the available power
            P_a = self.thrust_to_power(T, V)

            # Convert to brake power

            # Add to total energy

            # Store everything
            y_lst.append(y)
            x_lst.append(x)
            vy_lst.append(vy)
            vx_lst.append(vx)
            th_lst.append(th)
            T_lst.append(T)
            t_lst.append(t)
            ax_lst.append(ax/self.g)
            ay_lst.append(ay/self.g)

            # Check if end conditions are satisfied
            if t >= 200:
                running = False

        plt.subplot(221)
        plt.plot(t_lst, np.degrees(np.array(th_lst)))

        plt.subplot(222)
        plt.plot(t_lst, vx_lst)

        plt.subplot(223)
        plt.plot(t_lst, T_lst)

        plt.subplot(224)
        plt.plot(x_lst, y_lst)
        plt.show()

        return distance, energy, time

    def total_energy(self):

        # Get the energy and distance needed to reach cruise
        d_climb, E_climb, t_climb = self.numerical_simulation()

        # Get the energy and distance needed to descend
        d_desc, E_desc, t_desc = self.numerical_simulation()

        # Distance spent in cruise
        d_cruise = self.mission_dist - d_desc - d_climb

        # Cruise speed
        V_cruise = 60

        # Get the energy used in cruise

        # Get the total energy consumption
        E_tot = 1

        # Mission time
        t_tot = t_climb + t_desc + d_cruise / V_cruise

        return E_tot

a = mission()
a.numerical_simulation()
a.total_energy()

