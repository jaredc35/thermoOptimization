import streamlit as st
from expanders import *
from scipy.optimize import fsolve
from equations import thermal_resistance_cylinder


init_power = 250 * 10 ** 6
run_time = 54*30*86400



# Define the equation
def equation(t):
    return (0.0622 * init_power * (t**(-0.2)-(run_time + t)**(-0.2))) - 3.9345 * 10 ** 5

# Initial guess
initial_guess = 1.0


# Use fsolve to find the root
# solution = fsolve(equation, initial_guess)

# print("Solution for t:", solution[0]/86400)

st.set_page_config(page_title="Blue Energy", page_icon=":radioactive_sign:")

st.header("Ocean Assumptions")
ocean_expander()

st.header("Monopile Sizes")
monopile_expander()

st.header("RX Assumptions")
rx_expander()


st.header("CNV Assumptions")
cnv_expander()

# st.write(st.session_state)


st.header("Thermal Conductivities")
K_monopile = st.number_input("Monopile W/(m*C)", value=16.2)
K_grout = st.number_input("Grout Material (W/mC): ", value=0.8)

st.header("Heat Transfer Coefficients")
h_ocean = st.number_input("Ocean Heat Transfer Coefficient (W/m^2*C): ", value=300)

st.header("Heat Loss Calculations")
# st.write("Thermal Resistance of Inner Monopile: ", 
#          thermal_resistance_cylinder(innerPileOuterRadius, innerPileInnerRadius,
#                                      K_monopile, monopileHeight))
# st.write("Thermal Resistance of Spacing: ", 
#          thermal_resistance_cylinder(outerPileInnerRadius, innerPileOuterRadius,
#                                      K_grout, monopileHeight))
# st.write("Thermal Resistance of Outer Monopile: ", 
#          thermal_resistance_cylinder(outerPileOuterDiameter, outerPileInnerRadius,
#                                      K_grout, monopileHeight))


