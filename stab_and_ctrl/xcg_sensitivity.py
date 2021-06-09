import numpy as np
from scipy import optimize
from matplotlib import pyplot as plt


def xcg_stab(CLfa, CLra, CLf, CLr, Af, Ar, ef, er, xf, xr, zf, zr, zcg,
             Vr_Vf_2, Sr_Sf, de_da):
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


def find_mac_and_cr(S, b, taper):
    cavg = S / b
    cr = 2 / (1 + taper) * cavg
    mac = 2/3 * cr * (1 + taper + taper ** 2) / (1 + taper)
    return mac, cr


def stab_sensitivity():
    Cmacf = -0.0645
    Cmacr = -0.0645
    CLfmax = 1.44333
    CLrmax = 1.44333
    CLfdes = 0.7382799
    CLrdes = 0.7382799
    CD0f = 0.00822
    CD0r = 0.00822
    Af = 9
    Ar = 9
    taper = 0.45
    Lambda_c4 = 0
    ef = 0.958
    er = 0.958
    Clfa = 6.1879
    Clra = 6.1879
    cf = 1.014129367767935
    cr = 1.014129367767935
    zf = 0.5
    zr = 1.2
    zcg = 0.7
    Vr_Vf_2 = 0.8
    Sr_Sf = 1
    elev_fac = 1.4

    rho = 1.225
    Pbr = 110024/1.2 * 0.9 /12
    S = 8.417113787320769 * 2
    W = 2939.949692*9.80665

    # variables calculated based on the the parameters above
    xf = 1 / 4 * cf + 0.5
    xr = 7.2 - 3 / 4 * cr - 0.5
    Sf = S / (1 + Sr_Sf)
    Sr = S / (1 + Sr_Sf)
    lambda_c2 = lambda_c4_to_lambda_c2(Af, taper, 0)
    bf = np.sqrt(Sf * Af)
    CLfa = CLa(Clfa, Af, lambda_c2)
    CLra = CLa(Clra, Ar, lambda_c2)

    res = 1000
    xf_range = np.linspace(0, 3, res)
    xr_range = np.linspace(5, 7.5, res)
    zf_range = np.linspace(0, 1.5, res)
    zr_range = np.linspace(0.5, 2.5, res)
    Sr_Sf_range = np.linspace(0, 4, res)
    Af_range = np.linspace(1, 15, res)
    Ar_range = np.linspace(1, 15, res)

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
    cf_range = cf * np.sqrt(Sf / Af_range) / np.sqrt(Sf / Af)
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
    cr_range = cr * np.sqrt(Sr / Ar_range) / np.sqrt(Sr / Ar)
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

    plt.figure()
    Sr_Sf_grid, Af_grid = np.meshgrid(Sr_Sf_range, Af_range)
    Sf_grid = S / (1 + Sr_Sf_grid)
    bf_grid = np.sqrt(Sf_grid * Af_grid)
    cf_grid = cf * np.sqrt(Sf_grid / Af_grid) / np.sqrt(Sf / Af)
    Sr_grid = S - Sf_grid
    br_grid = np.sqrt(Sr_grid * Ar)
    cr_grid = cr * np.sqrt(Sr_grid / Ar) / np.sqrt(Sr / Ar)
    CLfa_grid = CLa(Clfa, Af_grid, lambda_c2)
    de_da = deps_da(Lambda_c4, bf_grid, xr - xf, zr - zf, Af_grid,
                    CLfa_grid, rho, Pbr, Sf_grid, CLfdes, W)
    x_cg_stab = xcg_stab(CLfa_grid, CLra, CLfdes, CLrdes, Af_grid, Ar, ef,
                         er, xf, xr, zf, zr, zcg, Vr_Vf_2, Sr_Sf_grid, de_da)
    x_cg_ctrl = xcg_ctrl(Cmacf, Cmacr, CLfmax * elev_fac, CLrmax, CD0f, CD0r,
                         Af_grid, Ar, ef, er, cf_grid, cr_grid, xf, xr, zf,
                         zr, zcg, Vr_Vf_2, Sr_Sf_grid)
    # plt.pcolormesh(Sr_Sf_grid, Af_grid, x_cg_stab - x_cg_ctrl, vmin=-1.5, vmax=1.5, cmap="coolwarm")
    plt.pcolormesh(Sr_Sf_grid, Af_grid, bf_grid, cmap="rainbow")
    plt.colorbar()
    # plt.contour(Sr_Sf_grid, Af_grid, x_cg_stab - x_cg_ctrl, [0], colors=["tab:blue"])

    xcg_rear = 3.1
    xcg_front = 2.9
    cf_max = 2
    cr_max = 2
    bf_min = 4
    br_max = 14

    plt.contour(Sr_Sf_grid, Af_grid, x_cg_stab, [xcg_rear], colors=["tab:purple"])  # needs to be on the right of this
    plt.contour(Sr_Sf_grid, Af_grid, x_cg_ctrl, [xcg_front], colors=["tab:brown"])  # needs to be on the left of this
    plt.contour(Sr_Sf_grid, Af_grid, cf_grid, [cf_max], colors=["tab:orange"])  # needs to be above this
    plt.contour(Sr_Sf_grid, Af_grid, cr_grid, [cr_max], colors=["tab:green"])  # needs to be on the left of this
    plt.contour(Sr_Sf_grid, Af_grid, bf_grid, [bf_min], colors=["tab:red"])  # needs to be above this
    plt.contour(Sr_Sf_grid, Af_grid, br_grid, [br_max], colors=["tab:pink"])  # needs to be on the left of this

    plt.xlabel("Sr/Sf")
    plt.ylabel("Af")

    plt.show()


def cost(Cmacf, Cmacr, CLmaxf, CLmaxr, CLdesf, CLdesr, CD0f, CD0r,
         taperf, taperr, lambda_c4f, lambda_c4r, ef, er, Claf, Clar,
         zcg, Vr_Vf_2, elev_fac, rho, Pbr, S, W, xrangef,
         xranger, zrangef, zranger, crmaxf, crmaxr, bmaxf, bmaxr,
         xcgrange, Af, Ar, xf, xr, zf, zr, Sr_Sf, inf=1e6):

    if not xrangef[0] < xf < xrangef[1] or not xranger[0] < xr < xranger[1]:
        return inf

    if not zrangef[0] < zf < zrangef[1] or not zranger[0] < zr < zranger[1]:
        return inf

    Sf = S / (1 + Sr_Sf)
    Sr = S - Sf
    bf = np.sqrt(Sf * Af)
    br = np.sqrt(Sr * Ar)

    if bf > bmaxf or br > bmaxr:
        return inf

    macf, crf = find_mac_and_cr(Sf, bf, taperf)
    macr, crr = find_mac_and_cr(Sr, br, taperr)

    if crf > crmaxf or crr > crmaxr:
        return inf

    lambda_c2f = lambda_c4_to_lambda_c2(Af, taperf, lambda_c4f)
    lambda_c2r = lambda_c4_to_lambda_c2(Ar, taperr, lambda_c4r)
    CLaf = CLa(Claf, Af, lambda_c2f)
    CLar = CLa(Clar, Ar, lambda_c2r)
    de_da = deps_da(lambda_c4f, bf, xr - xf, zr - zf,
                    Af, CLaf, rho, Pbr, Sf, CLdesf, W)
    xstab = xcg_stab(CLaf, CLar, CLdesf, CLdesr, Af, Ar, ef, er, xf, xr,
                     zf, zr, zcg, Vr_Vf_2, Sr_Sf, de_da)
    xctrl = xcg_ctrl(Cmacf, Cmacr, CLmaxf * elev_fac, CLmaxr, CD0f,
                     CD0r, Af, Ar, ef, er, macf, macr, xf, xr, zf, zr,
                     zcg, Vr_Vf_2, Sr_Sf)

    if xstab < xcgrange[1] or xctrl > xcgrange[0]:
        return inf

    return 1/bf


def optimise_wings(Cmacf, Cmacr, CLmaxf, CLmaxr, CLdesf, CLdesr, CD0f, CD0r,
                   taperf, taperr, lambda_c4f, lambda_c4r, ef, er, Claf, Clar,
                   zcg, Vr_Vf_2, elev_fac, rho, Pbr, S, W, xrangef,
                   xranger, zrangef, zranger, crmaxf, crmaxr, bmaxf, bmaxr,
                   xcgrange, init_Af=5, init_Ar=10, init_xf=0.5, init_xr=6.5,
                   init_zf=0.5, init_zr=1.5, init_Sr_Sf=1):
    # FIXME: span efficiency factor is assumed to be constant
    """
    Optimise for maximum wingspan on the front wing while meeting stability
    and controllability requirements and structural constraints.

    Parameters to be optimised:
        - Aspect ratios of both wings
        - x-positions of both wings
        - z-positions of both wings
        - Sr/Sf (relative size of the wings)

    Constraints:
        - Allowable x-range for both wings
        - Allowable z-range for both wings
        - Maximum root chord for both wings
        - Maximum wingspan for both wings
        - Minimum x-position of rear CG
        - Maximum x-position of front CG

    Optimisation goal:
        - Maximise wingspan of the front wing

    :param Cmacf:
    :param Cmacr:
    :param CLmaxf:
    :param CLmaxr:
    :param CLdesf:
    :param CLdesr:
    :param CD0f:
    :param CD0e:
    :param taperf:
    :param taperr:
    :param lambda_c4f:
    :param lambdac4:
    :param r:
    :param ef:
    :param er:
    :param Claf:
    :param Clar:
    :param zcg:
    :param Vr_Vf_2:
    :param elev_fac:
    :param rho:
    :param Pbr:
    :param S:
    :param W:
    :param xrangef:
    :param xranger:
    :param zrangef:
    :param zranger:
    :param crmaxf:
    :param crmaxr:
    :param bmaxf:
    :param bmaxr:
    :param xcgrange:
    :return:
    """
    x0 = np.array([init_Af, init_Ar, init_xf, init_xr,
                   init_zf, init_zr, init_Sr_Sf])

    def costfunc(x):
        Af, Ar, xf, xr, zf, zr, Sr_Sf = x
        return cost(Cmacf, Cmacr, CLmaxf, CLmaxr, CLdesf, CLdesr, CD0f, CD0r,
                    taperf, taperr, lambda_c4f, lambda_c4r, ef, er, Claf,
                    Clar, zcg, Vr_Vf_2, elev_fac, rho, Pbr, S, W, xrangef,
                    xranger, zrangef, zranger, crmaxf, crmaxr, bmaxf, bmaxr,
                    xcgrange, Af, Ar, xf, xr, zf, zr, Sr_Sf)

    result = optimize.minimize(costfunc, x0)
    print(result)

    if not result.success:
        return None

    return result.x


if __name__ == "__main__":
    Cmacf = -0.0645
    Cmacr = -0.0645
    CLfmax = 1.44333
    CLrmax = 1.44333
    CLfdes = 0.7382799
    CLrdes = 0.7382799
    CD0f = 0.00822
    CD0r = 0.00822
    Af = 9
    Ar = 9
    taper = 0.45
    Lambda_c4 = 0
    ef = 0.958
    er = 0.958
    Clfa = 6.1879
    Clra = 6.1879
    zcg = 0.7
    Vr_Vf_2 = 0.8
    Sr_Sf = 1
    elev_fac = 1.4
    rho = 1.225
    Pbr = 110024 / 1.2 * 0.9 / 12
    S = 8.417113787320769 * 2
    W = 2939.949692 * 9.80665

    xf = [0, 2.5]
    xr = [4.5, 7]
    zf = [0, 1]
    zr = [1, 1.7]
    crmaxf = 2
    crmaxr = 2.5
    bmax = 14
    xcgrange = [2.9, 3.1]

    print(optimise_wings(Cmacf, Cmacr, CLfmax, CLrmax, CLfdes, CLrdes, CD0f,
                         CD0r, taper, taper, Lambda_c4, Lambda_c4, ef, er,
                         Clfa, Clra, zcg, Vr_Vf_2, elev_fac, rho, Pbr, S, W,
                         xf, xr, zf, zr, crmaxf, crmaxf, bmax, bmax, xcgrange))
