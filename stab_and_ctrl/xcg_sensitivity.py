import numpy as np
from matplotlib import pyplot as plt


def xcg_stab(CLfa, CLra, CLf, CLr, Af, Ar, ef, er, xf, xr, zf, zr, zcg, Vr_Vf_2,
             Sr_Sf, de_da):
    num = (2 * CLf / (np.pi * Af * ef) * CLfa * (zcg - zf)
           - 2 * CLr / (np.pi * Ar * er) * CLra * (zr - zcg) * (1 - de_da)
           + CLfa * xf
           + CLra * xr * Vr_Vf_2 * Sr_Sf * (1 - de_da))

    den = CLfa + CLra * Vr_Vf_2 * Sr_Sf * (1 - de_da)

    return num / den


def deps_da(Lambda_quarter_chord, b, lh, h_ht, A, CLaw, rho, Pbr, Sf, CLf, W):
    r = lh * 2 / b
    mtv = h_ht * 2 / b  # Approximation
    Keps = (0.1124 + 0.1265 * Lambda_quarter_chord + 0.1766 * Lambda_quarter_chord ** 2) / r ** 2 + 0.1024 / r + 2
    Keps0 = 0.1124 / r ** 2 + 0.1024 / r + 2
    v = 1 + (r ** 2 / (r ** 2 + 0.7915 + 5.0734 * mtv ** 2)) ** (0.3113)
    de_da = Keps / Keps0 * CLaw / (np.pi * A) * (
            r / (r ** 2 + mtv ** 2) * 0.4876 / (np.sqrt(r ** 2 + 0.6319 + mtv ** 2)) + v * (
            1 - np.sqrt(mtv ** 2 / (1 + mtv ** 2))))
    phi = np.arcsin(mtv/r)
    dsde_da = np.where(
        np.logical_and(np.rad2deg(phi) < 30, np.rad2deg(phi) > 0),
        6.5*(rho*Pbr**2*Sf**3*CLf**3/(lh**4*W**3))**(1/4)*(np.sin(phi*6))**2.5,
        0
    )

    return de_da+dsde_da


def xcg_ctrl(Cmacf, Cmacr, CLf, CLr, CD0f, CD0r, Af, Ar, ef, er, cf, cr, xf,
             xr, zf, zr, zcg, Vr_Vf_2, Sr_Sf):
    num = (-Cmacf
           - Cmacr * Vr_Vf_2 * Sr_Sf * cr/cf
           + CLf * xf/cf
           + CLr * xr/cf * Vr_Vf_2 * Sr_Sf
           + (CD0f + CLf**2 / (np.pi * Af * ef)) * (zcg - zf) / cf
           - (CD0r + CLr**2 / (np.pi * Ar * er)) * (zr - zcg) / cf * Vr_Vf_2 * Sr_Sf)

    den = CLf / cf + CLr / cf * Vr_Vf_2 * Sr_Sf

    return num / den


def stab_sensitivity():
    CLfa = 5.1685
    CLra = 5.1685
    Cmacf = -0.0645
    Cmacr = -0.0645
    CLf = 1.781
    CLr = 1.737
    CD0f = 0.03254
    CD0r = 0.03254
    Af = 10
    Ar = 10
    ef = 0.958
    er = 0.958
    cf = 0.65
    cr = 0.65
    xf = 0.5
    xr = 7
    zf = 0.5
    zr = 1.7
    zcg = 0.7
    Vr_Vf_2 = 0.8
    Sr_Sf = 1

    rho = 1.225
    Pbr = 110024/1.2 * 0.9 /16
    S = 10.5
    Sf = S / 2
    Lambda_c4 = 0
    bf = np.sqrt(Sf * Af)
    W = 3652.352770706565*9.80665

    xf_range = np.linspace(0, 3)
    xr_range = np.linspace(5, 7.5)
    zf_range = np.linspace(0, 1.5)
    zr_range = np.linspace(1.5, 3)
    Sr_Sf_range = np.linspace(0.3, 3)

    plt.subplot(221)
    plt.title("xf")
    de_da = deps_da(Lambda_c4, bf, xr - xf_range, zr - zf, Af, CLfa, rho, Pbr,
                    Sf, CLf, W)
    print(de_da)
    x_cg_stab = xcg_stab(CLfa, CLra, CLf, CLr, Af, Ar, ef, er, xf_range, xr,
                         zf, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLf, CLr, CD0f, CD0r, Af, Ar, ef, er,
                         cf, cr, xf_range, xr, zf, zr, zcg, Vr_Vf_2, Sr_Sf)
    plt.axvline(xf)
    plt.plot(xf_range, x_cg_stab)
    plt.plot(xf_range, x_cg_ctrl)

    plt.subplot(222)
    plt.title("xr")
    de_da = deps_da(Lambda_c4, bf, xr_range - xf, zr - zf, Af, CLfa, rho, Pbr,
                    Sf, CLf, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLf, CLr, Af, Ar, ef, er, xf, xr_range,
                         zf, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLf, CLr, CD0f, CD0r, Af, Ar, ef, er,
                         cf, cr, xf, xr_range, zf, zr, zcg, Vr_Vf_2, Sr_Sf)
    plt.axvline(xr)
    plt.plot(xr_range, x_cg_stab)
    plt.plot(xr_range, x_cg_ctrl)

    plt.subplot(223)
    plt.title("zf")
    de_da = deps_da(Lambda_c4, bf, xr - xf, zr - zf_range, Af, CLfa, rho, Pbr,
                    Sf, CLf, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLf, CLr, Af, Ar, ef, er, xf, xr,
                         zf_range, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLf, CLr, CD0f, CD0r, Af, Ar, ef, er,
                         cf, cr, xf, xr, zf_range, zr, zcg, Vr_Vf_2, Sr_Sf)
    plt.axvline(zf)
    plt.plot(zf_range, x_cg_stab)
    plt.plot(zf_range, x_cg_ctrl)

    plt.subplot(224)
    plt.title("zr")
    de_da = deps_da(Lambda_c4, bf, xr - xf, zr_range - zf, Af, CLfa, rho, Pbr,
                    Sf, CLf, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLf, CLr, Af, Ar, ef, er, xf, xr, zf,
                         zr_range, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLf, CLr, CD0f, CD0r, Af, Ar, ef, er,
                         cf, cr, xf, xr, zf, zr_range, zcg, Vr_Vf_2, Sr_Sf)
    plt.axvline(zr)
    plt.plot(zr_range, x_cg_stab)
    plt.plot(zr_range, x_cg_ctrl)

    plt.figure()
    plt.title("Sr/Sf")
    # FIXME: this assumes that the MAC is equal to the average chord
    Sf_range = S * Sr_Sf_range ** (-1) / (1 + Sr_Sf_range ** (-1))
    cf_range = np.sqrt(Sf_range / Af)
    Sr_range = S - Sf_range
    cr_range = np.sqrt(Sr_range / Ar)
    de_da = deps_da(Lambda_c4, bf, xr - xf, zr - zf, Af, CLfa, rho, Pbr,
                    Sf_range, CLf, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLf, CLr, Af, Ar, ef, er, xf, xr, zf, zr,
                         zcg, Vr_Vf_2, Sr_Sf_range, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLf, CLr, CD0f, CD0r, Af, Ar, ef, er,
                         cf_range, cr_range, xf, xr, zf, zr, zcg, Vr_Vf_2,
                         Sr_Sf_range)
    plt.axvline(Sr_Sf)
    plt.plot(Sr_Sf_range, x_cg_stab)
    plt.plot(Sr_Sf_range, x_cg_ctrl)
    plt.show()


if __name__ == "__main__":
    stab_sensitivity()
