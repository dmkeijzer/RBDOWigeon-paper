
# Weights of the criteria
weights = {"Specific energy density": 1,
           "Volumetric energy density": 1,
           "Power density": 1,
           "Safety score": 1,
           "Operational life": 1,
           "Cost": 1}

# List of batteries
li_ion = {"Specific energy density": 1,
          "Volumetric energy density": 1,
          "Power density": 1,
          "Safety score": 1,
          "Operational life": 1,
          "Cost": 1}

li_S = {"Specific energy density": 1,
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
    return weights["Specific energy density"]*system["Specific energy density"] + \
           weights["Volumetric energy density"]*system["Volumetric energy density"] + \
           weights["Power density"]*system["Power density"] + \
           weights["Safety score"]*system["Safety score"] + \
           weights["Operational life"]*system["Operational life"] + \
           weights["Cost"]*(1/system["Cost"])


print("Trade-off scores:")
print("Lithium ion:", score(li_ion))
print("Lithium-sulfur:", score(li_S))
print("Solid state:", score(solid_st))
print("Hydrogen fuel cell:", score(H2_fuelcell))
