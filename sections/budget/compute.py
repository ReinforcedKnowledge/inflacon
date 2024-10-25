import pandas as pd


def retrieve_inflation_rates(
    inflation_data: pd.DataFrame, time_variation: str
) -> pd.Series:
    """Retrieve inflation rates based on time variation."""
    column = (
        "Monthly_Inflation_Rate"
        if time_variation == "Variation Mensuelle"
        else "Annual_Inflation_Rate"
    )
    return inflation_data[column]


def compute_adjusted_budget(
    budget_data: pd.DataFrame, inflation_rates: pd.Series
) -> pd.DataFrame:
    """Compute the adjusted budget based on current budget and inflation rates."""
    budget_data["Budget ajusté à l'inflation"] = budget_data["Budget"] * (
        1 + inflation_rates
    )
    return budget_data


def compute_and_update_budget(inflation_data, session_state):
    """Compute adjusted budget and update session state. Used when we change the time variation through the radio widget."""
    time_variation = session_state["inflation_variation_type"]
    inflation_rates = retrieve_inflation_rates(inflation_data, time_variation)
    session_state["budget_data"] = compute_adjusted_budget(
        session_state["budget_data"], inflation_rates
    )


def update_budget_data(inflation_data, session_state):
    """Update both budget and adjusted budget by recomputing it. Used when we edit the data editor itself."""
    print("HERE WE ARE")
    session_state["budget_data"].update(
        pd.DataFrame.from_dict(
            session_state["budget_editor"]["edited_rows"], orient="index"
        )
    )
    compute_and_update_budget(inflation_data, session_state)
