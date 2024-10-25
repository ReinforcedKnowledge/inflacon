import re
import unicodedata
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.constants import get_region_product_type_mapping


def sanitize_filename(filename: str) -> str:
    filename = unicodedata.normalize("NFD", filename)
    filename = filename.encode("ascii", "ignore").decode("utf-8")
    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9_]", "", filename)
    return filename


def load_data(
    region: str = "France",
    household: str = "Ensemble des ménages",
    index_type: str = "IPC",
    nomenclature_type: str = "NonNomenclature",
    variation_type: str = "None",
) -> pd.DataFrame:
    data_folder = Path("data")
    filename = f"{household}_{region}_{index_type}_{variation_type}_{nomenclature_type}"
    filename = sanitize_filename(filename) + ".csv"
    inflation_data = pd.read_csv(data_folder / filename)
    return inflation_data


def get_target_cols_for_month_year(
    month: int, year: int
) -> tuple[str, str, str]:
    previous_year = year - 1

    target_column = f"{year}-{month:02d}"
    if f"{month:02d}" == "01":
        previous_month_column = f"{previous_year}-12"
    else:
        previous_month = f"{month - 1:02d}"
        previous_month_column = f"{year}-{previous_month}"
    same_month_last_year_column = f"{previous_year}-{month:02d}"

    return (
        target_column,
        previous_month_column,
        same_month_last_year_column,
    )


def check_data_availability_conditions(
    data: pd.DataFrame, month: int, year: int
) -> bool:
    required_columns = {*get_target_cols_for_month_year(month, year)}
    if not required_columns.issubset(data.columns):
        return False
    if data[list(required_columns)].isna().any().any():
        return False
    return True


def get_last_date_with_available_data(
    data: pd.DataFrame, month: int, year: int
) -> tuple[int, int]:
    current_month, current_year = month, year
    while not check_data_availability_conditions(
        data, current_month, current_year
    ):
        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1
    return current_month, current_year


def filter_data_per_month_year(
    data: pd.DataFrame, month: int | None, year: int | None
) -> tuple[int, int, pd.DataFrame]:
    month, year = (month or date.today().month), (year or date.today().year)
    return (
        month,
        year,
        data[["Libellé"] + [*get_target_cols_for_month_year(month, year)]],
    )


def force_filter_data_per_month_year(
    data: pd.DataFrame, month: int | None, year: int | None
) -> tuple[int, int, pd.DataFrame]:
    month, year = (month or date.today().month), (year or date.today().year)
    if not check_data_availability_conditions(data, month, year):
        last_month, last_year = get_last_date_with_available_data(
            data, month, year
        )
        st.warning(
            f"Nous ne disposons pas des données pour {year}-{month:02d}. Nous allons utiliser celles de {last_year}-{last_month:02d}.",
        )
        return (
            last_month,
            last_year,
            data[
                ["Libellé"]
                + [*get_target_cols_for_month_year(last_month, last_year)]
            ],
        )
    return (
        month,
        year,
        data[
            ["Libellé"]
            + [*get_target_cols_for_month_year(last_month, last_year)]
        ],
    )


def normalize_by_libelle_column(
    inflation_data: pd.DataFrame, region: str
) -> pd.DataFrame:
    region_mapping = get_region_product_type_mapping()[region]
    inflation_data["Libellé"] = (
        inflation_data["Libellé"].str.split(" - ").str[-1].str.strip()
    )
    inflation_data["Libellé"] = inflation_data["Libellé"].map(region_mapping)
    inflation_data = (
        inflation_data.dropna(subset=["Libellé"])
        .drop_duplicates(subset=["Libellé"])
        .reset_index(drop=True)
    )
    return inflation_data


def get_product_type_data_by_region_for_month_year(
    product_type: str, region: str, month: int, year: int
) -> pd.DataFrame:
    region_data = load_data(region)
    _, _, region_data = filter_data_per_month_year(region_data, month, year)
    region_data = normalize_by_libelle_column(region_data, region)
    return region_data[region_data["Libellé"] == product_type]


def order_libelle_like_insee(inflation_data: pd.DataFrame) -> pd.DataFrame:
    insee_order = [
        "Ensemble",
        "Alimentation",
        "Produits frais",
        "Autre alimentation",
        "Tabac",
        "Produits manufacturés",
        "Habillement et chaussures",
        "Produits de santé",
        "Autres produits manufacturés",
        "Énergie",
        "dont Produits pétroliers",
        "Services",
        "Loyers, eau et enlèvement des ordures ménagères",
        "Services de santé",
        "Transports",
        "Communications",
        "Autres services",
    ]
    order_mapping = {name: i for i, name in enumerate(insee_order)}
    inflation_data["Libellé_order"] = inflation_data["Libellé"].map(
        order_mapping
    )
    inflation_data = (
        inflation_data.sort_values(by="Libellé_order")
        .drop(columns="Libellé_order")
        .reset_index(drop=True)
    )
    return inflation_data


@st.cache_data
def load_region_inflation_data(region="France"):
    inflation_data = load_data(region)

    month, year, inflation_data = force_filter_data_per_month_year(
        inflation_data, None, None
    )

    inflation_data = normalize_by_libelle_column(inflation_data, region)

    inflation_data = inflation_data.dropna(subset=["Libellé"])
    if region == "France Métropolitaine":
        tobacco_data = get_product_type_data_by_region_for_month_year(
            "Tabac", "France", month, year
        )
        inflation_data = pd.concat(
            [inflation_data, tobacco_data], ignore_index=True
        )

    target_column, previous_month_column, same_month_last_year_column = (
        get_target_cols_for_month_year(month, year)
    )
    inflation_data["Monthly_Inflation_Rate"] = (
        inflation_data[target_column] - inflation_data[previous_month_column]
    ) / inflation_data[previous_month_column]
    inflation_data["Annual_Inflation_Rate"] = (
        inflation_data[target_column]
        - inflation_data[same_month_last_year_column]
    ) / inflation_data[same_month_last_year_column]

    annual_inflation_rate = inflation_data.loc[
        inflation_data["Libellé"] == "Ensemble", "Annual_Inflation_Rate"
    ].values[0]

    inflation_data = order_libelle_like_insee(inflation_data)

    return (
        inflation_data,
        annual_inflation_rate,
    )
