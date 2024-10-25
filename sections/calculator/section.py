import streamlit as st

from sections.calculator.compute import (
    calculate_inflation_adjusted_salary,
    calculate_new_salary,
    register_region_change,
)
from sections.calculator.ui import region_change_selectbox, salary_input_section
from utils.config_utils import load_region_inflation_data


def load_calculator():
    st.title("Calculateur d'Inflation et de Pouvoir d'Achat")
    region = region_change_selectbox(
        "Choisissez votre département ou région :",
        [
            "France",
            "France Métropolitaine",
            "Guadeloupe",
            "Guyane",
            "La Réunion",
            "Martinique",
        ],
        "Nous ne disposons pas des données d'inflation sur le tabac pour la France Métropolitaine, nous utilisons celles à l'échelle de la France.",
        register_region_change,
    )
    inflation_data, annual_inflation_rate = load_region_inflation_data(region)
    st.subheader("Estimation de Salaire Ajusté à l'Inflation")
    st.write("")
    st.write(
        f"**Taux d'inflation actuel (annuel) :** {annual_inflation_rate * 100:.2f}%"
    )
    st.write("")
    _, salary_input = salary_input_section(
        "Format de salaire", "Entrez votre salaire actuel : ", ["Salaire en €"]
    )
    st.write("")
    new_salary_option, new_salary_input = salary_input_section(
        "Type d'Augmentation de Salaire",
        "Entrez le nombre correspondant ",
        ["Salaire en €", "Augmentation (%)"],
    )
    st.write("")

    new_salary = calculate_new_salary(
        salary_input, new_salary_input, new_salary_option
    )
    st.write(f"**Nouveau Salaire :** {new_salary:.2f}€")

    inflation_adjusted_salary = calculate_inflation_adjusted_salary(
        new_salary, annual_inflation_rate
    )
    st.write(
        f"**Salaire ajusté à l'inflation :** {inflation_adjusted_salary:.2f}€"
    )
    st.write("")
    return inflation_data
