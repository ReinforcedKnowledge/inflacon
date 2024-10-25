from math import ceil

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.config_utils import load_data, normalize_by_libelle_column

st.set_page_config(page_title="Inflation : Tableau de bord", layout="wide")


def generate_dash_styles(items):
    base_styles = ["solid", "dash", "dot", "dashdot", "longdash", "longdashdot"]
    # Repeat the base styles to match the number of items
    dash_styles = (base_styles * (len(items) // len(base_styles) + 1))[
        : len(items)
    ]
    return dict(zip(items, dash_styles))


plotly_config = {
    "displayModeBar": True,
    "modeBarButtonsToAdd": [],
    "modeBarButtonsToRemove": [],
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "plot",
        "scale": 2,
        "width": 1920,
        "height": 1080,
    },
}


@st.cache_data
def load_and_process_data(
    selected_regions,
    selected_household,
    selected_index_type,
    selected_variation_type,
    is_coicop,
):
    data_list = []
    nomenclature_type = "Nomenclature" if is_coicop else "NonNomenclature"
    for region in selected_regions:
        try:
            df = load_data(
                region=region,
                household=selected_household,
                index_type=selected_index_type,
                nomenclature_type=nomenclature_type,
                variation_type=selected_variation_type,
            )
        except FileNotFoundError:
            st.warning(f"Data file not found for {region}. Skipping.")
            continue

        df.columns = df.columns.str.strip()

        df = normalize_by_libelle_column(df, region)
        df["Region"] = region
        df["Household"] = selected_household
        df["IndexType"] = selected_index_type
        df["VariationType"] = selected_variation_type
        df["IsNomenclature"] = nomenclature_type == "Nomenclature"

        pattern = r"^(199[0-9]|20[0-9][0-9])-(0[1-9]|1[0-2])$"
        date_columns = df.columns[df.columns.str.match(pattern)]

        id_vars = [
            "Libellé",
            "Region",
            "Household",
            "IndexType",
            "VariationType",
            "IsNomenclature",
        ]
        df = df[id_vars + list(date_columns)]

        df_melted = df.melt(
            id_vars=id_vars,
            value_vars=date_columns,
            var_name="Date",
            value_name="Value",
        )

        df_melted["Date"] = pd.to_datetime(df_melted["Date"], format="%Y-%m")

        data_list.append(df_melted)

    if data_list:
        data = pd.concat(data_list, ignore_index=True)
    else:
        data = pd.DataFrame()

    return data


def expand_global_data(global_data, facet_col, unique_facets):
    expanded_global_data_list = []
    for facet_value in unique_facets:
        expanded_global_data = global_data.copy()
        expanded_global_data[facet_col] = facet_value
        expanded_global_data["IsGlobal"] = True
        expanded_global_data["Color"] = "Inflation Globale"
        expanded_global_data_list.append(expanded_global_data)
    expanded_global_data = pd.concat(
        expanded_global_data_list, ignore_index=True
    )
    return expanded_global_data


st.sidebar.header("Filtres")

all_regions = [
    "France",
    "France Métropolitaine",
    "Guadeloupe",
    "Martinique",
    "Guyane",
    "La Réunion",
]
selected_regions = st.sidebar.multiselect(
    "Sélectionnez les régions ou départements :",
    all_regions,
    default=["France"],
)

group_regions = st.sidebar.checkbox(
    "Voulez-vous grouper les graphes pour chaque région dans la même figure ?",
    value=True,
)

all_households = [
    "Ensemble des ménages",
    "Ménages du premier quintile de la distribution des niveaux de vie",
    "Ménages urbains dont le chef est ouvrier ou employé",
]
selected_household = st.sidebar.selectbox(
    "Sélectionnez le type de ménages :", all_households, index=0
)

all_index_types = [
    "IPC",
    "Indice CVS des prix à la consommation",
    "Indice d'inflation sous-jacente",
    "Secteurs conjoncturels",
]
selected_index_type = st.sidebar.selectbox(
    "Sélectionnez le type d'indice :", all_index_types, index=0
)

all_variation_types = ["None", "Glissement annuel", "Variations mensuelles"]
selected_variation_type = st.sidebar.selectbox(
    "Sélectionnez le type de variation :",
    all_variation_types,
    index=0,
    format_func=lambda x: x if x != "None" else "Aucune",
)


is_coicop = st.sidebar.checkbox(
    "Utilisez les produits de nomenclature COICOP ?",
    value=False,
)


data = load_and_process_data(
    selected_regions,
    selected_household,
    selected_index_type,
    selected_variation_type,
    is_coicop,
)

if data.empty:
    st.error("No data available for the selected filters.")
else:
    products = sorted(data["Libellé"].unique())
    default_products = ["Ensemble"] if "Ensemble" in products else products[:1]
    selected_products = st.sidebar.multiselect(
        "Sélectionnez les types de produits :",
        products,
        default=default_products,
    )

    min_date = data["Date"].min()
    max_date = data["Date"].max()
    start_date, end_date = st.sidebar.slider(
        "Sélectionnez une plage de temps :",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
        format="YYYY-MM",
    )

    include_global = st.sidebar.checkbox(
        "Inclure l'inflation globale ?",
        value=True,
    )

    comparison_mode = st.sidebar.radio(
        "Sélectionnez le mode de comparaison :",
        ["Superposée", "Côte à côte"],
    )

    filtered_data = data[
        (data["Libellé"].isin(selected_products))
        & (data["Date"] >= pd.to_datetime(start_date))
        & (data["Date"] <= pd.to_datetime(end_date))
    ]

    filtered_data["Value"] = pd.to_numeric(
        filtered_data["Value"], errors="coerce"
    )

    filtered_data = filtered_data.sort_values(by=["Region", "Libellé", "Date"])

    if include_global:
        global_data = load_and_process_data(
            ["France"],
            "Ensemble des ménages",
            "IPC",
            "None",
            False,
        )

        global_data = global_data[
            (global_data["Libellé"] == "Ensemble")
            & (global_data["Date"] >= pd.to_datetime(start_date))
            & (global_data["Date"] <= pd.to_datetime(end_date))
        ]
        global_data["Value"] = pd.to_numeric(
            global_data["Value"], errors="coerce"
        )
        global_data = global_data.sort_values(by=["Region", "Libellé", "Date"])

    if selected_variation_type in [
        "Glissement annuel",
        "Variations mensuelles",
    ]:
        y_axis_label = "Variation (%)"
    else:
        y_axis_label = "Indice"

    title = ""
    if selected_index_type == "IPC":
        title = "Indice des Prix à la Consommation"
    else:
        title += f"{selected_index_type}"
        if selected_variation_type != "None":
            title += f" - {selected_variation_type}"

    # Generate color and dash mappings
    unique_regions = filtered_data["Region"].unique()
    unique_products = filtered_data["Libellé"].unique()

    # Exclude 'red' from color sequence
    available_colors = [
        c for c in px.colors.qualitative.Set1 if c != "rgb(228,26,28)"
    ]
    if len(unique_regions) > len(available_colors):
        available_colors *= (len(unique_regions) // len(available_colors)) + 1
    region_colors = dict(
        zip(unique_regions, available_colors[: len(unique_regions)])
    )

    product_dashes = generate_dash_styles(unique_products)

    # Reserve 'red' for global data
    global_color = "red"

    if comparison_mode == "Superposée":
        if group_regions:
            fig_title = f"{title} au cours du temps"
            fig = px.line(
                filtered_data,
                x="Date",
                y="Value",
                color="Region",
                line_dash="Libellé",
                labels={
                    "Value": y_axis_label,
                    "Region": "Région",
                    "Libellé": "Catégorie",
                },
                title=fig_title,
                color_discrete_map=region_colors,
                line_dash_map=product_dashes,
            )
            if include_global:
                fig.add_trace(
                    go.Scatter(
                        x=global_data["Date"],
                        y=global_data["Value"],
                        mode="lines",
                        name="Inflation Globale",
                        showlegend=True,
                        line=dict(color=global_color),
                    )
                )
            st.plotly_chart(fig, use_container_width=True, config=plotly_config)
        else:
            product_colors = dict(
                zip(unique_products, available_colors[: len(unique_products)])
            )
            for region in selected_regions:
                region_data = filtered_data[filtered_data["Region"] == region]
                title_with_region = f"{region} - {title} au cours du temps"
                fig = px.line(
                    region_data,
                    x="Date",
                    y="Value",
                    color="Libellé",
                    labels={
                        "Value": y_axis_label,
                        "Region": "Région",
                        "Libellé": "Catégorie",
                    },
                    title=title_with_region,
                    color_discrete_map=product_colors,
                )
                if include_global:
                    fig.add_trace(
                        go.Scatter(
                            x=global_data["Date"],
                            y=global_data["Value"],
                            mode="lines",
                            name="Inflation Globale",
                            showlegend=True,
                            line=dict(color=global_color),
                        )
                    )
                st.plotly_chart(
                    fig, use_container_width=True, config=plotly_config
                )
    elif comparison_mode == "Côte à côte":
        if not group_regions:
            facet_col = "Region"
            color_col = "Libellé"
            color_mapping = dict(
                zip(unique_products, available_colors[: len(unique_products)])
            )
        else:
            facet_col = "Libellé"
            color_col = "Region"
            color_mapping = region_colors

        num_facets = filtered_data[facet_col].nunique()
        num_columns = 3
        num_rows = ceil(num_facets / num_columns)
        row_height = 400
        total_height = row_height * num_rows

        if include_global:
            unique_facets = filtered_data[facet_col].unique()
            global_data_expanded = expand_global_data(
                global_data, facet_col, unique_facets
            )

            filtered_data["IsGlobal"] = False
            filtered_data["Color"] = filtered_data[color_col].astype(str)
            global_data_expanded["IsGlobal"] = True
            global_data_expanded["Color"] = "Inflation Globale"
            filtered_data_combined = pd.concat(
                [filtered_data, global_data_expanded], ignore_index=True
            )
            color_mapping["Inflation Globale"] = global_color
        else:
            filtered_data_combined = filtered_data.copy()
            filtered_data_combined["Color"] = filtered_data_combined[
                color_col
            ].astype(str)
            filtered_data_combined["IsGlobal"] = False

        fig = px.line(
            filtered_data_combined,
            x="Date",
            y="Value",
            color="Color",
            facet_col=facet_col,
            facet_col_wrap=num_columns,
            labels={
                "Value": y_axis_label,
                "Region": "Région",
                "Libellé": "Catégorie",
                "Color": "Légende",
            },
            title=f"Évolution de {title} au cours du temps",
            height=total_height,
            color_discrete_map=color_mapping,
        )

        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        st.plotly_chart(fig, use_container_width=True, config=plotly_config)
