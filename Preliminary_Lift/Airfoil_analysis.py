import pandas as pd
import numpy as np


def airfoil_stats(df1, df2):
    print(df1)
    df1["cl/cd"] = df1["CL"]/df1["CD"]

    Clmax = np.max(df2["CL"])
    Cdmin = np.min(df1["CD"])
    Cl_Cdmin = np.average(df1["CL"][df1["CD"] == Cdmin])
    Cm = np.average(df1["Cm"][df1["CL"] == Cl_Cdmin])
    Clalpha =   (np.average(df1["CL"][df1["alpha"] == 3]) +np.average(df1["CL"][df1["alpha"] == -3]))/6
    clcdmax = np.max(df1["cl/cd"])
    Cl_maxld = np.average(df1["CL"][df1["cl/cd"] == clcdmax])
    a_clmax = np.average(df2["alpha"][df2["CL"] == Clmax])
    a_0L = -np.average(df1["CL"][df1["alpha"] ==0])/Clalpha

    return Clmax, Cdmin, Cl_Cdmin, Cm, Clalpha, clcdmax, Cl_maxld, a_clmax, a_0L
x = airfoil_stats(pd.read_csv("Airfoil_data/LS417_Re2.300.csv"), pd.read_csv("Airfoil_data/LS417_Re1.700.csv"))
print(x)