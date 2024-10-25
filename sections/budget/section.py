import pandas as pd
import streamlit as st

from sections.budget.compute import (
    compute_and_update_budget,
    update_budget_data,
)
from sections.budget.ui import (
    budget_editor,
    inflation_variation_radio_buttons,
    initialize_budget_editor_data,
)


def load_budget(inflation_data: pd.DataFrame) -> None:
    st.subheader("Prévision Budgétaire")
    st.write("")
    data_table_height = initialize_budget_editor_data(inflation_data)
    _ = inflation_variation_radio_buttons(
        "Choisissez le type de variation pour ajuster le budget à l'inflation :",
        ["Variation Annuelle", "Variation Mensuelle"],
        0,
        compute_and_update_budget,
        "inflation_variation_type",
        (inflation_data, st.session_state),
    )
    st.write("")
    if (
        "region_change" in st.session_state
        and st.session_state["region_change"]
    ):
        update_budget_data(inflation_data, st.session_state)
    st.write(
        "Entrez votre budget pour chaque catégorie et il sera ajusté en fonction de l'inflation."
    )
    _ = budget_editor(
        st.session_state["budget_data"],
        data_table_height,
        {
            "Catégories": st.column_config.Column(
                "Catégories", width="large", required=True
            ),
            "Budget": st.column_config.NumberColumn(
                "Budget (€)",
                min_value=0,
                format="%f",
                required=True,
            ),
            "Budget ajusté à l'inflation": st.column_config.NumberColumn(
                "Budget ajusté à l'inflation (€)",
                min_value=0,
                width="medium",
                format="%f",
                required=True,
            ),
        },
        ["Catégories", "Budget ajusté à l'inflation"],
        update_budget_data,
        "budget_editor",
        (inflation_data, st.session_state),
    )
