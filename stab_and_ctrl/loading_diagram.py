class CgCalculator:
    """
    Class to calculate the CG and generate loading diagrams for the aircraft.
    The coordinate system has its origin at the nose, and the x-axis points
    backwards. The y-axis points towards starboard.

    @author: Jakob Schoser
    """
    def __init__(self, m_wf: float, m_wr: float, m_fus: float, m_bat: float,
                 m_cargo: float, m_pax: float, m_pil: float, cg_fus: list,
                 cg_bat: list, cg_cargo: list, cg_pax: list, cg_pil: list):
        """
        Constructs a CG calculator object for a given aircraft. It takes the
        masses and CG of all components, except for the wings where the CG
        is not fixed since it will be optimised during the design for stability
        and control.
        :param m_wf: Mass of the front wing (incl. engines)
        :param m_wr: Mass of the rear wing (incl. engines)
        :param m_fus: Empty mass of the aircraft without the wings and battery
        :param m_bat: Mass of the battery
        :param m_cargo: Mass of the cargo
        :param m_pax: Mass of one passenger (incl. personal luggage)
        :param m_pil: Mass of the pilot
        :param cg_fus: [x, y]-location of the CG of m_fus
        :param cg_bat: [x, y]-location of the CG of the battery
        :param cg_cargo: [x, y]-location of the CG of the cargo
        :param cg_pax: [x, y]-locations of the CGs of all passengers in a list
        :param cg_pil: [x, y]-location of the CG of the pilot
        """
        self.m_wf = m_wf
        self.m_wr = m_wr
        self.m_fus = m_fus
        self.m_bat = m_bat
        self.m_cargo = m_cargo
        self.m_pax = m_pax
        self.m_pil = m_pil

        self.cg_fus = cg_fus
        self.cg_bat = cg_bat
        self.cg_cargo = cg_cargo
        self.cg_pax = cg_pax
        self.cg_pil = cg_pil

    def calc_cg(self, x_wf: float, x_wr: float, loaded_cargo: bool,
                seated_pax: list, seated_pil: bool) -> tuple:
        """
        Calculates the CG of the aircraft for given wing positions and
        occupied seats.
        :param x_wf: x-location of the CG of the front wing
        :param x_wr: x-location of the CG of the rear wing
        :param loaded_cargo: boolean indicating whether cargo has been loaded
        :param seated_pax: list of booleans indicating passenger presence
        :param seated_pil: boolean indicating whether pilot is seated
        :return: [x, y]-location of the CG of the aircraft
        """
        x = (self.m_wf * x_wf + self.m_wr * x_wr
             + self.m_fus * self.cg_fus[0] + self.m_bat * self.cg_bat[0])
        y = (self.m_fus * self.cg_fus[1] + self.m_bat * self.cg_bat[1])
        m = self.m_wf + self.m_wr + self.m_fus + self.m_bat

        if loaded_cargo:
            x += self.m_cargo * self.cg_cargo[0]
            y += self.m_cargo * self.cg_cargo[1]
            m += self.m_cargo

        for seated, cg in zip(seated_pax, self.cg_pax):
            if seated:
                x += self.m_pax * cg[0]
                y += self.m_pax * cg[1]
                m += self.m_pax

        if seated_pil:
            x += self.m_pil * self.cg_pil[0]
            y += self.m_pil * self.cg_pil[1]
            m += self.m_pil

        x /= m
        y /= m

        return x, y

    def calc_cg_range(self, x_wf: float, x_wr: float,
                      order=("cargo", "pil", 1, 2, 3, 4)) -> tuple:
        """
        Calculate the CG range during loading of the aircraft.
        :param x_wf: x-location of the CG of the front wing
        :param x_wr: x-location of the CG of the rear wing
        :param order: Order of loading different parts. May contain "cargo",
        "pil", and numbers indicating passenger IDs starting from 1.
        :return: [most forward CG, most aft CG],
        [most port CG, most starboard CG]
        """

        x_front, x_aft, y_port, y_star = None, None, None, None

        loaded_cargo = False
        seated_pax = [False for _ in order]
        seated_pil = False

        for item in order:
            if item == "cargo":
                loaded_cargo = True
            elif item == "pil":
                seated_pil = True
            else:
                seated_pax[item - 1] = True

            x, y = self.calc_cg(x_wf, x_wr, loaded_cargo,
                                seated_pax, seated_pil)

            if x_front is None:
                x_front, x_aft = x, x
                y_port, y_star = y, y
            else:
                x_front = min(x_front, x)
                x_aft = max(x_aft, x)

                y_port = min(y_port, y)
                y_star = max(y_star, y)

        return [x_front, x_aft], [y_star, y_port]
