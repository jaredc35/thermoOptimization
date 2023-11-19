import pandas as pd
import streamlit as st
import numpy as np
import math
from scipy.optimize import fsolve

#%% Database Setup
satWater = pd.read_csv("saturatedWater.csv")
satWater['P(atm)'] = satWater['P (MPa)'] * 9.86923
satWater.rename({
    "T (°C)":"T(C)",
    "Specific Volume Liquid (m^3/kg)":"SpecVolLiq",
    "Specific Volume Vapor (m^3/kg)":"SpecVolVap",
    "Internal Energy Liquid (kJ/kg)":"IntEngLiq",
    "Internal Energy Vapor (kJ/kg)":"IntEngVap",
    "Internal Energy of Vaporization (kJ/kg)":"IntEngDiff",
    "Enthalpy Liquid (kJ/kg)":"EnthLiq",
    "Enthalpy Vapor (kJ/kg)":"EnthVap",
    "Enthalpy of Vaporization":"EnthDiff",
    "Entropy Liquid [kJ/(kg K)]":"EntrLiq",
    "Entropy Vapor [kJ/(kg K)]":"EntrVap",
    "Entropy of Vaporization [kJ/(kg K)]":"EntrDiff"}, axis=1, inplace=True)

subWater = pd.read_csv("subcooledWater.csv")
subWater['P(atm)'] = subWater['Pressure (MPa)'] * 9.86923
subWater.rename(columns={
        " Temperature (°C)":"T(C)",
        " Specific Volume (m^3/kg)":"SpecVol",
        " Density (kg/m^3)":"Density",
        " Specific Internal Energy (kJ/kg)":"IntEng",
        " Specific Enthalpy (kJ/kg)":"Enth",
        "Pressure (MPa)":'P (MPa)',
        " Specific Entropy [kJ/(kg K)]":"Entr"}, inplace=True)

def getClosestValue(df, searchCol, value, returnCol):
    return df[returnCol][abs(df[searchCol]-value).idxmin()]


#%% Volumes
def cylindrical_volume(r, h):
    return math.pi*r**2*h

def waterVolumeInit(level):
    cnvVolume = cylindrical_volume(st.session_state.cnvDiameter/2, st.session_state.cnvHeight)
    if level > st.session_state.cnvHeight:
        return level*math.pi*st.session_state.innerPileInnerRadius**2 - cnvVolume
    else:
        return level * math.pi * (st.session_state.innerPileInnerRadius**2 - (st.session_state.cnvDiameter/2) ** 2)



#%% Thermal Resistances
def thermal_resistance_cylinder(rO, rI, k, L):
    return math.log(rO/rI)/(math.pi*2*k*L)

def thermal_resistance_ocean(h, r, L):
    return 1/(h*2*math.pi*r*L)


def integral(t, days=True):
    if days: t = t * 86400 # Convert time in days to seconds
    return 0.07775 * st.session_state.rxPower *(t**0.8 - (t+st.session_state.timeAtPower)**0.8)

def FahtoCel(f):
    return (f-32)*5/9



# Define the equation
def decayHeatEquation(t):
    return (0.0622 * st.session_state.rxPower * (t**(-0.2)-(st.session_state.timeAtPower + t)**(-0.2)))

def timeToNoBoiling(t):
    saturationTemp = getClosestValue(satWater, "P(atm)", st.session_state.reliefSetpoint, "T(C)") # Find saturation temp based on relief pressure
    heatLossThroughMonopile = (saturationTemp - FahtoCel(st.session_state.oceanTemp))/st.session_state.total_thermal_resistance
    return (0.0622 * st.session_state.rxPower * (t**(-0.2)-(st.session_state.timeAtPower + t)**(-0.2))) - heatLossThroughMonopile





def runCalcs():


    # Find Energy Required to heat water to boiling
    initialWaterVolume = waterVolumeInit(st.session_state.initialWaterLvl)
    massWater = 1/getClosestValue(satWater,'T(C)', FahtoCel(st.session_state.oceanTemp), 'SpecVolLiq') * initialWaterVolume
    saturationTemp = getClosestValue(satWater, "P(atm)", st.session_state.reliefSetpoint, "T(C)") # Find saturation temp based on relief pressure
    initialEnthalpy = getClosestValue(satWater, 'T(C)', FahtoCel(st.session_state.oceanTemp), 'EnthLiq') # Get enthalpy of liquid at subcooled temp
    boilingEnthalpy = getClosestValue(satWater, "T(C)", saturationTemp, "EnthLiq") # Get enthalpy of liquid at saturation temp
    vaporizatonEnthalpy = getClosestValue(satWater, "T(C)", saturationTemp, 'EnthDiff') # Get enthalpy of vaporization at saturation temp
    waterDensityatSat = 1/getClosestValue(satWater, "T(C)", saturationTemp, "SpecVolLiq") # Get water density at saturation temp
    energyToBoil = massWater * (boilingEnthalpy - initialEnthalpy) * 10**3
    volumeToTopCNV = math.pi * st.session_state.cnvHeight * (st.session_state.innerPileInnerRadius ** 2 - (st.session_state.cnvDiameter/2)**2)
    heatLossThroughMonopile = (saturationTemp - FahtoCel(st.session_state.oceanTemp))/st.session_state.total_thermal_resistance
    # Initial guess
    initial_guess = 1.0
    # Use fsolve to find the root
    dates = [1,2,3,4]
    dates.extend(range(5,151,5))
    solution = float(fsolve(timeToNoBoiling, initial_guess)/86400)
    dates.append(solution)
    dates.sort()
    df = pd.DataFrame(columns=['Days after S/D'], data=dates)

    
    
    
    # Assume 10 seconds for inital power released
    initialPowerReleased = integral(10, False)
    df['Difference (J)'] = integral(df['Days after S/D']) - initialPowerReleased

    df["Mass Evaporated (kg)"] = np.where(df['Difference (J)'] > energyToBoil, 
                                          (df['Difference (J)']-energyToBoil)/vaporizatonEnthalpy/1000, 
                                          0)
    # Sets mass evaporated = the mass evaporated when excess decay heat = 0
    df['Mass Evaporated (kg)'] = np.where(df['Days after S/D']>solution, float((df.loc[df['Days after S/D']==solution]['Mass Evaporated (kg)']).iloc[0]),
                                          df['Mass Evaporated (kg)'])
    # Find volume of water remaining
    df['Volume Remaining (m^3)'] = np.maximum((massWater-df['Mass Evaporated (kg)'])/waterDensityatSat, [0])

    # Find Water level remaining
    df['Water Level Remaining (m)'] = np.where(df['Volume Remaining (m^3)']>volumeToTopCNV, 
                                               st.session_state.cnvHeight + (df['Volume Remaining (m^3)']-volumeToTopCNV)/(math.pi*st.session_state.innerPileInnerRadius**2),
                                               df['Volume Remaining (m^3)']/(math.pi*(st.session_state.innerPileInnerRadius**2 - (st.session_state.cnvDiameter/2)**2))
    )
    df['Decay Heat Produced (W)'] = decayHeatEquation(df["Days after S/D"]*86400)
    df['Excess Decay Heat (kW)'] = np.maximum(df['Decay Heat Produced (W)']-heatLossThroughMonopile, [0])/1000
    return df, solution
