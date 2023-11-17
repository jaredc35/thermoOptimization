import streamlit as st
from equations import cylindrical_volume

default_state = {
    # Ocean State
    "oceanTemp":80,
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
    "cnvDiameter":15*.3048
}

# Initialize the state
for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

def ocean_expander():
    with st.expander("Ocean Characteristics"):
        st.slider("Ocean Temperature: ", value=st.session_state.oceanTemp, min_value=50, max_value=100, step=5, key="oceanTemp")

def monopile_expander():
    with st.expander("Monopile Characteristics"):
        col1, col2 = st.columns(2)
        with col1:
            st.slider("Outer monopile Diameter (m): ", value=st.session_state.outerMonopileOuterDiameter,
                      min_value=10., max_value=15., step=0.25, key="outerMonopileOuterDiameter")
            st.slider("Outer Monopile Thickness (m)", value=st.session_state.outerMonopileThickness,min_value=.10, max_value=.15, step=0.01, key="outerMonopileThickness")
            differentThickness = st.checkbox("Different Monopile Thicknesses?", value=False)
            if differentThickness:
                st.slider("Inner Monopile Thickness (m)", value=st.session_state.innerMonopileThickness, min_value=.10, max_value=.15, step=0.01, key="innerMonopileThickness")
            else:
                st.session_state.innerMonopileThickness = st.session_state.outerMonopileThickness
            st.slider("Monopile Spacing (m)", value=st.session_state.monopileSpacing, min_value=.10, max_value=.20, step=.01, key="monopileSpacing")
            st.slider("Monopile Height (m)", value=st.session_state.monopileHeight, min_value=20, max_value=40, step=1, key="monopileHeight")
        with col2: 
            st.session_state.outerPileOuterRadius = st.session_state.outerMonopileOuterDiameter / 2
            st.session_state.outerPileInnerRadius = st.session_state.outerPileOuterRadius - st.session_state.outerMonopileThickness
            st.session_state.innerPileOuterRadius = st.session_state.outerPileInnerRadius - st.session_state.monopileSpacing
            st.session_state.innerPileInnerRadius = st.session_state.innerPileOuterRadius - st.session_state.innerMonopileThickness
            st.write("Outer pile outer radius: {} m".format(round(st.session_state.outerPileOuterRadius, 2)))
            st.write("Outer pile inner radius: {} m".format(round(st.session_state.outerPileInnerRadius, 2)))
            st.write("Inner pile outer radius: {} m".format(round(st.session_state.innerPileOuterRadius,2)))
            st.write("Outer pile outer radius: {} m".format(round(st.session_state.innerPileInnerRadius, 2)))
            st.write("Volume of Inner Monopile: {}".format(round(cylindrical_volume(st.session_state.innerPileInnerRadius, st.session_state.monopileHeight))))
    # st.write(st.session_state)

def rx_expander():
    with st.expander("Reactor Assumptions"):
        st.session_state.rxPower = st.number_input("Reactor Power (MW): ", value=int(st.session_state.rxPower/10**6), key='rxPowerMW')*10**6
        st.session_state.timeAtPower = st.number_input("Time at power (Months): ", value=st.session_state.timeAtPower/30/86400, key='timeAtPowerMo')*30*86400

def cnv_expander():
    with st.expander("CNV Assumptions"):
        col1, col2 = st.columns(2)
        with col1: 
            st.session_state.cnvHeight = st.number_input("CNV Height (ft): ", value=st.session_state.cnvHeightft, key='cnvHeightft') * .3048
            st.session_state.cnvDiameter = st.number_input("CNV Diameter (ft): ", value=st.session_state.cnvDiameterft, key='cnvDiameterft') *.3048
        with col2: 
            st.write("CNV Height (m): {}".format(round(st.session_state.cnvHeight, 2)))
            st.write("CNV Diameter (m): {}".format(round(st.session_state.cnvDiameter, 2)))
            st.write("CNV Volume (m^3): {}".format(round(cylindrical_volume(st.session_state.cnvDiameter/2, st.session_state.cnvHeight), 2)))