import streamlit as st

from sections.budget.section import load_budget
from sections.calculator.section import load_calculator

st.set_page_config(page_title="Calculateur")


st.markdown(
    """
    <style>
    div[role="alert"] {
        background-color: #4d8c8e; /* #1593bd, #42BFF5 Change this to your desired background color */
        color: #FFFFFF;  /* Change this to your desired text color */
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Calculator section
inflation_data = load_calculator()

# Budget section
load_budget(inflation_data)


# At this point we consider that the region didn't change
st.session_state["region_change"] = False
