import numpy as np
import matplotlib.pyplot as plt
from Aero_tools import ISA


class mission:
    """
    This class simulates the take-off and landing af a tilt-wing eVTOL. Hover, transition and horizontal flight are
    all considered together, no distinction is made between the phases up to and after cruise.

    !!!!! THIS FILE STILL CONTAINS PLACEHOLDER VALUES TO TEST ITS FUNCTIONALITY. REMOVE BEFORE OPTIMIZING DESIGNS !!!!!
    TBD:
        - Add energy estimation
        - Add aerodynamic data  (Lift and drag curves)
        - Add propulsion data   (Thrust-to-power, max thrust)
        - Cruise performance
        - Descend performance
    """
    def __init__(self):

        # Temporary placeholders, REMOVE BEFORE RUNNING OPTIMIZATION
        self.a = 2 * np.pi
        self.mission_dist = 300e8
        self.S = 10
        self.g = 9.80665
        self.m = 2000
        self.max_rot = np.radians(5)

        # Design variables
        self.ax_target_climb = 0.5*self.g
        self.ay_target_climb = 0.1*self.g

        self.ax_target_descend = -0.2*self.g
        self.ay_target_descend = -0.1*self.g

        self.roc = 5
        self.rod = 5

        self.h_cruise = 300
        self.v_cruise = 60

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

        return ((-D*np.cos(gamma) - L*np.sin(gamma) + T*np.cos(th)) - self.m*ax_tgt,
                (L*np.cos(gamma) - self.m*self.g - D*np.sin(gamma) + T*np.sin(th)) - self.m*ay_tgt)

    def target_accelerations(self, vx, vy, y, y_tgt, vx_tgt, climb):

        # Target accelerations when climbing
        if climb:

            # Re-set the target values, such that the conditions below have to be re-evaluated each time
            ay_tgt = self.ay_target_climb
            ax_tgt = self.ax_target_climb

            # Distance needed to slow down the rate of climb
            d_rc = vy / ay_tgt

            # Check if target values have been reached
            if np.abs(vx - vx_tgt) < 5:
                ax_tgt = -0.5 * (vx - vx_tgt)

            # Do not start transition when altitude< 10 m for safety
            if y < 10:
                ax_tgt = 0

            if vy >= self.roc:
                ay_tgt = 0

            # Start reducing the R/C when approaching the cruising altitude
            if y >= y_tgt - d_rc:
                ay_tgt = -self.ay_target_climb

                # If within 5 meters of the target altitude,
                # change to a proportional-differential control of acceleration,
                # for smooth arrival and passenger comfort
                if np.abs(y - y_tgt) < 10:
                    ay_tgt = -0.05 * (y - y_tgt) - 0.5 * vy

        # Accelerations while descending
        else:
            ax_tgt = self.ax_target_descend
            ay_tgt = self.ay_target_descend

            # Vertical distance needed to cancel horizontal speed
            d_vert  = vy/ay_tgt

            # Limit rate-of-descend
            if abs(vy) >= self.rod:
                ay_tgt = 0

            # Check if target speed has been reached
            if np.abs(vx - vx_tgt) < 5:
                ax_tgt = -0.5 * (vx - vx_tgt)

            if y <= y_tgt + d_vert:

                # Start slowing down when getting close to the target altitude
                ay_tgt = -self.ay_target_descend

                # Again switch to a PID controller when nearing the target altitude
                if np.abs(y - y_tgt) < 10:
                    ay_tgt = -0.05 * (y - y_tgt) - 0.5 * vy

        return ax_tgt, ay_tgt

    def numerical_simulation(self, vx_start, y_start, th_start, y_tgt):

        # Initialization
        vx = vx_start
        vy = 0
        t = 0
        x = 0
        T = 0
        y = y_start
        th = th_start
        dt = 0.01

        # Check whether the aircraft needs to climb or descend
        if y_start > y_tgt:
            climb   = False
            vx_tgt  = 0
        else:
            climb   = True
            vx_tgt  = self.v_cruise

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

            # Get the target accelerations
            ax_tgt, ay_tgt = self.target_accelerations(vx, vy, y, y_tgt, vx_tgt, climb)

            # If a constraint on rotational speed is added, calculate the limits in rotation
            th_min, th_max  = th - self.max_rot*dt, th + self.max_rot*dt
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

            # Perform numerical integration
            vx  += ax*dt
            vy  += ay*dt

            x   += vx*dt
            y   += vy*dt

            # Prevent going underground
            y   = np.maximum(y, 0)

            # Store everything
            y_lst.append(y)
            x_lst.append(x)
            vy_lst.append(vy)
            vx_lst.append(vx)
            th_lst.append(th)
            T_lst.append(T)
            t_lst.append(t)
            ax_lst.append(ax)
            ay_lst.append(ay)

            # Check if end conditions are satisfied
            if abs(vx - vx_tgt) < 0.5 and abs(y - y_tgt) < 1 and abs(vy) < 0.5:
                running = False
                
        # Convert everything to arrays
        y_arr   = np.array(y_lst)
        x_arr   = np.array(x_lst)
        vy_arr  = np.array(vy_lst)
        vx_arr  = np.array(vx_lst)
        th_arr  = np.array(th_lst)
        T_arr   = np.array(T_lst)
        t_arr   = np.array(t_lst)
        ax_arr  = np.array(ax_lst)
        ay_arr  = np.array(ay_lst)
        V_arr   = np.sqrt(vx_arr**2 + vy_arr**2)

        # ======= Get Required outputs =======

        # Get the available power
        P_a = self.thrust_to_power(T_arr, V_arr)

        # Convert to brake power
        P_r = P_a/0.95  # IMPLEMENT EFFICIENCY

        # Add to total energy

        fig, ax1 = plt.subplots()
        ax1.plot(t_arr, np.degrees(th_arr), c = 'orange')
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Wing angle")

        ax2 = ax1.twinx()
        ax2.plot(t_arr, T_arr)
        ax2.set_xlabel("Time [s]")
        ax2.set_ylabel("Thrust")

        plt.tight_layout()
        plt.grid()
        plt.show()

        plt.subplot(221)
        plt.plot(t_arr, vx_arr)
        plt.xlabel("Time [s]")
        plt.ylabel("horizontal speed")

        plt.subplot(222)
        plt.plot(x_arr, y_arr)
        plt.xlabel("Distance")
        plt.ylabel("Altitude")

        plt.subplot(223)
        plt.plot(t_arr, vy_arr)
        plt.xlabel("Time [s]")
        plt.ylabel("roc")

        plt.subplot(224)
        plt.plot(t_arr, ay_arr/self.g)
        plt.xlabel("Time [s]")
        plt.ylabel("y-acceleration")

        plt.tight_layout()
        plt.show()

        distance = x_lst[-1]
        energy   = np.sum(P_r*dt)
        time     = t

        return distance, energy, time
    
    def cruise(self):

        # Density at cruising altitude
        rho     = ISA(self.h_cruise).density()

        # Lift coefficient during cruise, based on the cruise speed (can be non-optimal)
        CL_cruise   = 2*self.m*self.g/(self.v_cruise*self.v_cruise*self.S*rho)

        # Drag coefficient !!!!! UPDATE !!!!!
        CD_cruise   = 0.05
        eff_cruise  = 0.95

        P_cruise    = CD_cruise*self.m*self.g*self.v_cruise/(CL_cruise*eff_cruise)

        return P_cruise

    def total_energy(self):

        # Get the energy and distance needed to reach cruise
        d_climb, E_climb, t_climb = self.numerical_simulation(vx_start = 0.001, y_start = 0,
                                                              th_start = np.pi/2, y_tgt = 300)

        # Get the energy and distance needed to descend
        d_desc, E_desc, t_desc = self.numerical_simulation(vx_start = 60, y_start = 300, th_start = 0, y_tgt = 10)

        # Distance spent in cruise
        d_cruise = self.mission_dist - d_desc - d_climb

        # Time spent cruising
        t_cruise = d_cruise/self.v_cruise

        # Get the brake power used in cruise
        P_cruise = self.cruise()

        # Cruise energy
        E_cruise = P_cruise*t_cruise

        # Get the total energy consumption
        E_tot = E_cruise + E_climb + E_desc

        # Mission time
        t_tot = t_climb + t_desc + t_cruise

        # Pie chart
        labels  = ['Take-off', 'Cruise', 'Landing']
        Energy  = [E_climb, E_cruise, E_desc]
        Time    = [t_climb, t_cruise, t_desc]

        plt.subplot(211)
        plt.pie(Energy, labels = labels, autopct='%1.1f%%')

        plt.subplot(212)
        plt.pie(Time, labels = labels, autopct='%1.1f%%')

        plt.tight_layout()
        plt.show()

        return E_tot, t_tot


a = mission()

# Simulate descend
a.numerical_simulation(vx_start = 60, y_start = 300, th_start = 0, y_tgt = 0)

# Simulate climb
a.numerical_simulation(vx_start = 0.001, y_start = 0, th_start = np.pi/2, y_tgt = 300)

