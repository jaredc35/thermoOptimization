import streamlit as st
from expanders import *
from equations import *
import plotly.express as px
import numpy as np
import math


init_power = 250 * 10 ** 6
run_time = 54*30*86400



# print("Solution for t:", solution[0]/86400)
default_state = {
    # Ocean State
    "oceanTemp":80,
    "reliefSetpoint":1.,
    "initialWaterLvl":18.,
    # Monopile State
    "outerMonopileOuterDiameter": 12.,
    "outerMonopileThickness": .12,
    "innerMonopileThickness": .12,
    "monopileSpacing":.15,
    "monopileHeight":30,
    # RX State
    "rxPower":250*10**6,
    "timeAtPower":54*30*86400,
    "firstTime":10,
    # CNV State
    "cnvHeightft": 75.8,
    "cnvHeight": 75.8*.3048,
    "cnvDiameterft": 15,
    "cnvDiameter":15*.3048,
    # Thermal Properties
    "k_monopile":16.2,
    "k_grout":0.8,
    "h_ocean":300,
}

# Initialize the state
for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value


st.set_page_config(page_title="Decay Heat", page_icon=":radioactive_sign:",layout='wide')

col1, col2 = st.columns([1,2])

with col1: 
    st.header("Ocean Assumptions")
    ocean_expander()

    st.header("Monopile Sizes")
    monopile_expander()

    st.header("RX Assumptions")
    rx_expander()


    st.header("CNV Assumptions")
    cnv_expander()

    st.header("Thermal Conductivities")
    thermal_property_expander()

with col2:

    min_water_level = 8.5
  
    df, solution = runCalcs()
    maxLevel = math.ceil(df['Water Level Remaining (m)'].max()) + 2
    stableLevel = float((df.loc[df['Days after S/D']==solution]['Water Level Remaining (m)']).iloc[0])
    st.header("Water Level Remaining")
    df['color'] = np.where(df['Water Level Remaining (m)'] > min_water_level, 'blue', 'red')
    fig = px.scatter(df, x='Days after S/D', y='Water Level Remaining (m)', title='Water Level Remaining', range_y=[0, maxLevel], color='color', color_discrete_sequence=['cyan', 'red'])
    fig.add_hline(y=8.5, line_color='red')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig)
    st.write("After ",round(solution,1)," days, more heat lost through monopile than decay heat generated.  Temperatures begin cooling below boiling point.  Water level stabilized around ",
             round(stableLevel,1)," m.")
    st.dataframe(df[['Days after S/D', 'Mass Evaporated (kg)', 'Volume Remaining (m^3)', "Water Level Remaining (m)", "Decay Heat Produced (W)", 'Excess Decay Heat (kW)']])
    

# st.write(st.session_state)




# st.header("Heat Loss Calculations")


