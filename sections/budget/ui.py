import pandas as pd
import streamlit as st
from streamlit.elements.lib.column_types import ColumnConfig
from streamlit.runtime.state.session_state_proxy import SessionStateProxy


def initialize_budget_editor_data(
    inflation_data, num_categories: int = 17, ROW_HEIGHT: int = 37
):
    """_summary_

    Args:
        inflation_data (_type_): _description_
        num_categories (int, optional): Categories we find on the cyclical INSEE reports. Defaults to 17.
        ROW_HEIGHT (int, optional): Height of a row in the editor. Defaults to 38.
    """
    if "budget_data" not in st.session_state:
        st.session_state["budget_data"] = pd.DataFrame(
            {
                "Catégories": inflation_data["Libellé"],
                "Budget": [0.0] * num_categories,
            }
        )
        st.session_state["budget_data"]["Budget ajusté à l'inflation"] = 0.0
    return num_categories * ROW_HEIGHT


def inflation_variation_radio_buttons(
    label: str,
    options: list[str],
    default_index: int,
    on_time_variation_change: callable,
    state_key_name: str,
    widget_args: tuple[pd.DataFrame, SessionStateProxy],
):
    inflation_rate_time = st.radio(
        label,
        options,
        index=default_index,
        on_change=on_time_variation_change,
        horizontal=True,
        key=state_key_name,
        args=widget_args,
    )
    return inflation_rate_time


def budget_editor(
    budget_data: pd.DataFrame,
    data_table_height: int,
    column_config: dict[str, ColumnConfig],
    disabled_cols: list[str],
    on_budget_change: callable,
    state_key_name: str,
    widget_args: tuple[pd.DataFrame, SessionStateProxy],
):
    edited_data = st.data_editor(
        budget_data,
        height=data_table_height,
        hide_index=True,
        column_config=column_config,
        disabled=disabled_cols,
        key=state_key_name,
        on_change=on_budget_change,
        args=widget_args,
    )
    return edited_data
