import math

def thermal_resistance_cylinder(rO, rI, k, L):
    return math.log(rO/rI)/(math.pi*2*k*L)