import streamlit as st


def register_region_change():
    if "region_change" in st.session_state:
        st.session_state["region_change"] = True
    else:
        # We don't consider it a change of the region if it's done before even loading up the last part
        st.session_state["region_change"] = False


def calculate_new_salary(
    current_salary: float, new_salary_input: float, option: str
) -> float:
    """Calculate the new salary based on whether the user provided the raw new salary or a percentage increase."""
    if option == "Salaire en €":
        return new_salary_input
    if option == "Augmentation (%)":
        augmentation = new_salary_input / 100
        return current_salary + (current_salary * augmentation)


def calculate_inflation_adjusted_salary(
    new_salary: float, inflation_rate: float
) -> float:
    return new_salary / (1 + inflation_rate)
