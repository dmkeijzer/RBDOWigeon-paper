"""
Trade-off of the power system
"""

# Weights of the criteria
weights = {"Specific energy density": 1,
           "Volumetric energy density": 0.8,
           "Power density": 0.8,
           "Safety score": 0.5,
           "Operational life": 0.3,
           "Cost": 0.3}

# List of power system options
li_ion = {"Specific energy density": 250,
          "Volumetric energy density": 1,
          "Power density": 1,
          "Safety score": 1,
          "Operational life": 1,
          "Cost": 1}

li_S = {"Specific energy density": 350,
        "Volumetric energy density": 1,
        "Power density": 1,
        "Safety score": 1,
        "Operational life": 1,
        "Cost": 1}

solid_st = {"Specific energy density": 1,
            "Volumetric energy density": 1,
            "Power density": 1,
            "Safety score": 1,
            "Operational life": 1,
            "Cost": 1}

H2_fuelcell = {"Specific energy density": 1,
               "Volumetric energy density": 1,
               "Power density": 1,
               "Safety score": 1,
               "Operational life": 1,
               "Cost": 1}


def score(system):
    return weights["Specific energy density"]*system["Specific energy density"] / li_ion["Specific energy density"] + \
           weights["Volumetric energy density"]*system["Volumetric energy density"] / li_ion["Volumetric energy density"] + \
           weights["Power density"]*system["Power density"] / li_ion["Power density"] + \
           weights["Safety score"]*system["Safety score"] / li_ion["Safety score"] + \
           weights["Operational life"]*system["Operational life"] / li_ion["Operational life"] + \
           weights["Cost"]*(1/system["Cost"]) / (1/li_ion["Cost"])


print("Trade-off scores:")
print("Lithium ion:", score(li_ion))
print("Lithium-sulfur:", score(li_S))
print("Solid state:", score(solid_st))
print("Hydrogen fuel cell:", score(H2_fuelcell))
