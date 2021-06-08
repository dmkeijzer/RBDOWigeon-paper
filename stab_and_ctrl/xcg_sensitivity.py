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


def deps_da(lambda_c4, b, lh, h_ht, A, CLfa, rho, Pbr, Sf, CLfdes, W):
    r = lh * 2 / b
    mtv = h_ht * 2 / b  # Approximation
    Keps = (0.1124 + 0.1265 * lambda_c4 + 0.1766 * lambda_c4 ** 2) / r ** 2 + 0.1024 / r + 2
    Keps0 = 0.1124 / r ** 2 + 0.1024 / r + 2
    v = 1 + (r ** 2 / (r ** 2 + 0.7915 + 5.0734 * mtv ** 2)) ** (0.3113)
    de_da = Keps / Keps0 * CLfa / (np.pi * A) * (
            r / (r ** 2 + mtv ** 2) * 0.4876 / (np.sqrt(r ** 2 + 0.6319 + mtv ** 2)) + v * (
            1 - np.sqrt(mtv ** 2 / (1 + mtv ** 2))))
    phi = np.arcsin(mtv/r)
    dsde_da = np.where(
        np.logical_and(np.rad2deg(phi) < 30, np.rad2deg(phi) > 0),
        6.5*(rho*Pbr**2*Sf**3*CLfdes**3/(lh**4*W**3))**(1/4)*(np.sin(phi*6))**2.5,
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


def CLa(Cla, A, lambda_c2, M=0, eta=0.95):
    beta = np.sqrt(1 - M ** 2)
    value = Cla * A / (2 + np.sqrt(4 + ((A * beta / eta) ** 2) * (1 + (np.tan(lambda_c2) / beta) ** 2)))
    return value


def lambda_c4_to_lambda_c2(A, taper, lambda_c4):
    tanSweep_c4 = np.tan(lambda_c4)
    tanSweep_c2 = tanSweep_c4 - 4/A*(50-25)/100*(1-taper)/(1+taper)
    return np.arctan(tanSweep_c2)


def stab_sensitivity():
    Cmacf = -0.0645
    Cmacr = -0.0645
    CLfmax = 1.781
    CLrmax = 1.737
    CLfdes = 0.82
    CLrdes = 0.82
    CD0f = 0.03254
    CD0r = 0.03254
    Af = 10
    Ar = 10
    taper = 0.45
    Lambda_c4 = 0
    lambda_c2 = lambda_c4_to_lambda_c2(Af, taper, 0)
    ef = 0.958
    er = 0.958
    Clfa = 6
    Clra = 6
    CLfa = CLa(Clfa, Af, lambda_c2)
    CLra = CLa(Clra, Ar, lambda_c2)
    cf = 0.65
    cr = 0.65
    xf = 1/4 * cf
    xr = 7.2 - 3/4 * cr
    zf = 0
    zr = 1.705
    zcg = 0.7
    Vr_Vf_2 = 1
    Sr_Sf = 1
    elev_fac = 1.4

    rho = 1.225
    Pbr = 110024/1.2 * 0.9 /12
    S = 10.5
    Sf = S / 2
    Sr = S - Sf
    bf = np.sqrt(Sf * Af)
    W = 3652.352770706565*9.80665

    xf_range = np.linspace(0, 3)
    xr_range = np.linspace(5, 7.5)
    zf_range = np.linspace(0, 1.5)
    zr_range = np.linspace(1.5, 3)
    Sr_Sf_range = np.linspace(0, 2.5)
    Af_range = np.linspace(1, 20)
    Ar_range = np.linspace(1, 20)

    plt.subplot(221)
    plt.title("xf")
    de_da = deps_da(Lambda_c4, bf, xr - xf_range, zr - zf, Af, CLfa, rho, Pbr,
                    Sf, CLfdes, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLfdes, CLrdes, Af, Ar, ef, er, xf_range,
                         xr, zf, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLfmax * elev_fac, CLrmax, CD0f, CD0r,
                         Af, Ar, ef, er, cf, cr, xf_range, xr, zf, zr, zcg,
                         Vr_Vf_2, Sr_Sf)
    plt.axvline(xf)
    plt.plot(xf_range, x_cg_stab)
    plt.plot(xf_range, x_cg_ctrl)

    plt.subplot(222)
    plt.title("xr")
    de_da = deps_da(Lambda_c4, bf, xr_range - xf, zr - zf, Af, CLfa, rho, Pbr,
                    Sf, CLfdes, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLfdes, CLrdes, Af, Ar, ef, er, xf,
                         xr_range, zf, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLfmax * elev_fac, CLrmax, CD0f, CD0r,
                         Af, Ar, ef, er, cf, cr, xf, xr_range, zf, zr, zcg,
                         Vr_Vf_2, Sr_Sf)
    plt.axvline(xr)
    plt.plot(xr_range, x_cg_stab)
    plt.plot(xr_range, x_cg_ctrl)

    plt.subplot(223)
    plt.title("zf")
    de_da = deps_da(Lambda_c4, bf, xr - xf, zr - zf_range, Af, CLfa, rho, Pbr,
                    Sf, CLfdes, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLfdes, CLrdes, Af, Ar, ef, er, xf, xr,
                         zf_range, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLfmax * elev_fac, CLrmax, CD0f, CD0r,
                         Af, Ar, ef, er, cf, cr, xf, xr, zf_range, zr, zcg,
                         Vr_Vf_2, Sr_Sf)
    plt.axvline(zf)
    plt.plot(zf_range, x_cg_stab)
    plt.plot(zf_range, x_cg_ctrl)

    plt.subplot(224)
    plt.title("zr")
    de_da = deps_da(Lambda_c4, bf, xr - xf, zr_range - zf, Af, CLfa, rho, Pbr,
                    Sf, CLfdes, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLfdes, CLrdes, Af, Ar, ef, er, xf, xr, zf,
                         zr_range, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLfmax * elev_fac, CLrmax, CD0f, CD0r,
                         Af, Ar, ef, er, cf, cr, xf, xr, zf, zr_range, zcg,
                         Vr_Vf_2, Sr_Sf)
    plt.axvline(zr)
    plt.plot(zr_range, x_cg_stab)
    plt.plot(zr_range, x_cg_ctrl)

    plt.figure()
    plt.title("Sr/Sf")
    # FIXME: this assumes that the aerodynamic centre stays constant
    #  even if the wing area changes
    Sf_range = S / (1 + Sr_Sf_range)
    bf_range = np.sqrt(Sf_range * Af)
    cf_range = cf * np.sqrt(Sf_range / Af) / np.sqrt(Sf / Af)
    Sr_range = S - Sf_range
    cr_range = cr * np.sqrt(Sr_range / Ar) / np.sqrt(Sr / Ar)
    de_da = deps_da(Lambda_c4, bf_range, xr - xf, zr - zf, Af, CLfa, rho, Pbr,
                    Sf_range, CLfdes, W)
    x_cg_stab = xcg_stab(CLfa, CLra, CLfdes, CLrdes, Af, Ar, ef, er, xf, xr,
                         zf, zr, zcg, Vr_Vf_2, Sr_Sf_range, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLfmax * elev_fac, CLrmax, CD0f, CD0r,
                         Af, Ar, ef, er, cf_range, cr_range, xf, xr, zf, zr,
                         zcg, Vr_Vf_2, Sr_Sf_range)
    plt.axvline(Sr_Sf)
    plt.plot(Sr_Sf_range, x_cg_stab)
    plt.plot(Sr_Sf_range, x_cg_ctrl)

    plt.figure()
    plt.subplot(211)
    plt.title("Af")
    bf_range = np.sqrt(Sf * Af_range)
    cf_range = cf * np.sqrt(Sf / Af_range) / np.sqrt(Sf / Af_range)
    CLfa_range = CLa(Clfa, Af_range, lambda_c2)
    de_da = deps_da(Lambda_c4, bf_range, xr - xf, zr - zf, Af_range,
                    CLfa_range, rho, Pbr, Sf, CLfdes, W)
    x_cg_stab = xcg_stab(CLfa_range, CLra, CLfdes, CLrdes, Af_range, Ar, ef,
                         er, xf, xr, zf, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLfmax * elev_fac, CLrmax, CD0f, CD0r,
                         Af_range, Ar, ef, er, cf_range, cr, xf, xr, zf,
                         zr, zcg, Vr_Vf_2, Sr_Sf)
    plt.axvline(Af)
    plt.plot(Af_range, x_cg_stab)
    plt.plot(Af_range, x_cg_ctrl)

    plt.subplot(212)
    plt.title("Ar")
    cr_range = cr * np.sqrt(Sr / Ar_range) / np.sqrt(Sr / Ar_range)
    CLra_range = CLa(Clra, Ar_range, lambda_c2)
    de_da = deps_da(Lambda_c4, bf, xr - xf, zr - zf, Af,
                    CLfa, rho, Pbr, Sf, CLfdes, W)
    x_cg_stab = xcg_stab(CLfa, CLra_range, CLfdes, CLrdes, Af, Ar_range, ef,
                         er, xf, xr, zf, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLfmax * elev_fac, CLrmax, CD0f, CD0r,
                         Af, Ar_range, ef, er, cf, cr_range, xf, xr, zf,
                         zr, zcg, Vr_Vf_2, Sr_Sf)
    plt.axvline(Ar)
    plt.plot(Ar_range, x_cg_stab)
    plt.plot(Ar_range, x_cg_ctrl)

    plt.show()


if __name__ == "__main__":
    stab_sensitivity()
