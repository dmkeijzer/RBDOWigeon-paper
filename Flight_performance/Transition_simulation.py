import numpy as np
import matplotlib.pyplot as plt
import json
from Aero_tools import ISA
import scipy.optimize as optimize

class transition_EOM:
    def __init__(self, W):
        #self.V = V
        self.k = 0.9
        self.TA = 200
        self.rho = ISA(0).density()
        #self.a_T0 = a_T0
        #self.V_perp = np.cos(a_T0)*V
        self.CL = 1.0
        #self.q  = 0.5*self.rho*V*V
        self.W  = W
        self.S = 20
        self.T_h = 0
        self.P_max = 700000
        self.CD0 = 0.05
        self.A  = 10
        self.e = 0.98
        self.g_force = 0.5
        self.m = self.W/9.81
        self.A_prop = 10

    def disk_power(self, T, P_in, a_T, V):

        V_perp = V*np.cos(a_T)

        # Calculate the power provided by the rotating cruise engines
        P = T*V_perp + self.k*T*(-V_perp/2 + np.sqrt(V_perp**2/4 + T/(2*self.rho*self.A_prop))) - P_in

        return P

    def max_thrust(self, motor_AoA, speed):

        # Find the thrust for a certain input power and speed
        T = optimize.newton(self.disk_power, 10000, args = (self.P_max, motor_AoA, speed, ))

        return T

    def horizontal_equilibrium(self, motor_angle, speed, thrust):

        # Drag force
        D = 0.5*self.rho*(speed**2)*self.S*(self.CD0 + ((self.CL**2)/(self.A*self.e*np.pi)))


        # Acceleration in x (positive in direction of V)
        a_x = (-D + thrust*np.cos(motor_angle))/self.m

        return a_x

    def vertical_equilibrium(self, motor_angle, speed, thrust):

        # Lift force
        L = 0.5*self.rho*speed*speed*self.S*self.CL

        # Acceleration in y (vertical direction, positive upwards)
        a_y = (L + np.sin(motor_angle)*thrust - self.W)/self.m

        return a_y

    def thrust_vertical(self, motor_angle, speed):

        # Lift force
        L       = 0.5 * self.rho * speed * speed * self.S * self.CL

        thrust  = (self.W - L)/np.sin(motor_angle)

        return thrust

    def thrust_horizontal(self, motor_angle, speed):

        # Drag force
        D       = 0.5 * self.rho * speed * speed * self.S * (self.CD0 + ((self.CL ** 2) / (self.A * self.e * np.pi)))

        thrust  = D/np.cos(motor_angle)

        return thrust

    def simulate(self):

        # Initial values
        t   = 0.
        dt  = 0.1
        vx  = 0.     # Horizontal speed
        vy  = 0.     # Vertical speed
        v   = 0.#np.array([[0], [0]], dtype = 'float64')
        x   = 0.#np.array([[0], [0]], dtype = 'float64')     # horizontal position
        y   = 0.     # Vertical position
        V   = 0.
        i_T = np.pi/2
        a_T = i_T
        a = 0
        # List to store state variables
        V_lst   = []
        t_lst   = []
        x_lst   = []
        y_lst   = []
        i_lst   = []
        E_lst   = []

        # Main loop
        running = True
        while running:

            t   += dt

            # Maximum thrust
            T_max   = self.max_thrust(a_T, V)

            # Engine thrust setting for vertical equilibrium, or to maintain speed
            T_vert  = self.thrust_vertical(i_T, V)
            T_hor   = self.thrust_horizontal(i_T, V)

            T_req   = T_vert

            # In the beginning op transition the motors are rotated with a constant speed
            if T_vert < T_max:
                T   = T_vert
                i_T -= 2*np.pi*dt/180

            # If the required thrust is higher than the maximum thrust, wait for the speed to increase
            else:
                T   = T_max

            # Power used
            P   = self.disk_power(T, 0, a_T, V)

            i_T     = max(i_T, 0)

            # Numerical integration
            print('T', T)
            ax = self.horizontal_equilibrium(i_T, v, T)
            ay = self.vertical_equilibrium(i_T, V, T)

            vx += ax*dt
            vy += ay*dt

            x += vx*dt
            y += vy*dt

            V       = np.sqrt(vx**2  + vy**2)

            alpha   = np.arctan(vy/(vx+1e-9))
            a_T     = i_T + alpha



            # Store everything
            V_lst.append(V)
            t_lst.append(t)
            x_lst.append(x)
            y_lst.append(y)
            i_lst.append(i_T)
            E_lst.append(P*dt)


            if t > 100 or i_T == 0:
                running = False

        plt.subplot(311)
        plt.plot(t_lst, x_lst)
        plt.grid()

        plt.subplot(312)
        plt.plot(t_lst, V_lst)
        plt.grid()

        plt.subplot(313)
        plt.plot(t_lst, i_lst)
        plt.grid()

        plt.show()
        print("Total energy needed: ", sum(E_lst))


trans = transition_EOM(18000)
trans.simulate()
