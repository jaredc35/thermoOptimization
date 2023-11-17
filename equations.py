import math

def cylindrical_volume(r, h):
    return math.pi*r**2*h


def thermal_resistance_cylinder(rO, rI, k, L):
    return math.log(rO/rI)/(math.pi*2*k*L)