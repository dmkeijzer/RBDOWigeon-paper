g = 9.81  # [m/s^2]

oem = 2000  # [kg]
cg_oem = 2  # [kg]

m_pax = 95  # [kg]
m_pil = 80  # [kg]
m_fuel = 0  # [kg]

cg_seats = [
    2, 2,
    3, 3
]  # [m]
cg_pil = 1  # [m]
cg_fuel = 4  # [m]


def mass(pilot, seated, fuelled):
    return oem + pilot * m_pil + sum(seated) * m_pax + fuelled * m_fuel


def cg(pilot, seated, fuelled):
    x = pilot * m_pil * cg_pil + fuelled * m_fuel * cg_fuel
    for s, cg_seat in zip(seated, cg_seats):
        x += s * m_pax * cg_seat
    return x / mass(pilot, seated, fuelled)
