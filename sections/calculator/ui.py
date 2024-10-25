import streamlit as st


def region_change_selectbox(
    label: str, regions: list[str], help: str, on_region_change: callable
):
    col1, col2, col3 = st.columns((1, 2, 1))
    with col2:
        region = st.selectbox(
            label,
            regions,
            help="Nous ne disposons pas des données d'inflation sur le tabac pour la France Métropolitaine, nous utilisons celles à l'échelle de la France.",
            on_change=on_region_change,
        )
    return region


def salary_input_section(
    option_label: str,
    input_label: str,
    options: list[str],
    column_widths: tuple[int, int] = (3, 7),
) -> float:
    """Creates two columns for a salary input section. One column contains a selectbox for options,
    and the other contains a number input for salary entry.

    Args:
        option_label (str): Label for the selectbox.
        input_label (str): Label for the input.
        options (list[str]): List of options to display in the selectbox. They determine how the salary is represented.
        column_widths (tuple[int, int], optional): A tuple of two integers representing the width proportions of the columns.

    Returns:
        float: The value entered by the user in the number input field.
    """
    col1, col2 = st.columns(column_widths)
    with col1:
        salary_option = st.selectbox(option_label, options=options)
    with col2:
        salary_input = st.number_input(
            input_label, min_value=0.0, format="%.2f"
        )
    return salary_option, salary_input
