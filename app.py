
import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Interactive Map Visualization",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Interactive Map Visualization Examples")
st.write(
    "Explore different map visualization techniques "
    "using the Natural Earth countries dataset."
)


# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

@st.cache_data
def load_data():

    # Get the dataset folder relative to this Python file
    folder_path = (
        Path(__file__).resolve().parent
        / "ne_110m_admin_0_countries"
    )

    shapefile_path = (
        folder_path / "ne_110m_admin_0_countries.shp"
    )

    # Read shapefile
    gdf = gpd.read_file(shapefile_path)

    # Identify population column
    population_col = next(
        (col for col in gdf.columns if col.lower() == "pop_est"),
        None
    )

    # Use existing population data if available
    if population_col is not None:
        gdf["pop_est"] = gdf[population_col]
    else:
        np.random.seed(0)
        gdf["pop_est"] = np.random.randint(
            1e6, 1e9, size=len(gdf)
        )

    return gdf


gdf = load_data()


# --------------------------------------------------
# 3. SIDEBAR MENU
# --------------------------------------------------

st.sidebar.header("Choose a Map Type")

map_type = st.sidebar.radio(
    "Select Visualization:",
    [
        "Map Cosmetics",
        "Map Visual Hierarchy",
        "Choropleth Map",
        "Geo Projection"
    ]
)


# Identify country name column
country_col = next(
    (
        col for col in ["name", "NAME", "ADMIN"]
        if col in gdf.columns
    ),
    None
)


# --------------------------------------------------
# 4. MAP COSMETICS
# --------------------------------------------------

if map_type == "Map Cosmetics":

    st.header("1. Map Cosmetics")

    st.write(
        "Customize the appearance of the map using "
        "different colours, borders and backgrounds."
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    gdf.plot(
        ax=ax,
        color="skyblue",
        edgecolor="black",
        linewidth=0.5
    )

    ax.set_title(
        "Styled Map Example",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_facecolor("lightgrey")
    ax.set_axis_off()

    st.pyplot(fig)
    plt.close(fig)


# --------------------------------------------------
# 5. MAP VISUAL HIERARCHY
# --------------------------------------------------

elif map_type == "Map Visual Hierarchy":

    st.header("2. Map Visual Hierarchy")

    st.write(
        "Select countries to highlight them using a different "
        "colour from the remaining countries."
    )

    if country_col is None:
        st.error("Country name column not found in the dataset.")

    else:

        country_list = sorted(
            gdf[country_col].dropna().astype(str).unique()
        )

        default_countries = [
            "Brazil",
            "India",
            "China",
            "Australia",
            "South Africa",
            "Russia"
        ]

        # Only select default countries that exist in the dataset
        available_defaults = [
            country for country in default_countries
            if country in country_list
        ]

        selected_countries = st.multiselect(
            "Select countries to highlight:",
            country_list,
            default=available_defaults
        )

        # Assign colours based on selection
        gdf["color"] = gdf[country_col].apply(
            lambda country: (
                "red" if country in selected_countries
                else "skyblue"
            )
        )

        fig, ax = plt.subplots(figsize=(12, 7))

        gdf.plot(
            ax=ax,
            color=gdf["color"],
            edgecolor="black",
            linewidth=0.5
        )

        ax.set_title(
            "Map Visual Hierarchy - Highlighted Countries",
            fontsize=15,
            fontweight="bold"
        )

        ax.set_axis_off()

        st.pyplot(fig)
        plt.close(fig)


# --------------------------------------------------
# 6. CHOROPLETH MAP
# --------------------------------------------------

elif map_type == "Choropleth Map":

    st.header("3. Choropleth Map")

    st.write(
        "Visualize population density using different "
        "colour schemes and logarithmic scaling."
    )

    # Select colour scheme
    color_scheme = st.selectbox(
        "Choose Color Scheme:",
        ["OrRd", "YlGn", "Blues", "Purples", "Greens"]
    )

    # Select log scale option
    use_log_scale = st.checkbox(
        "Use Log Scale",
        value=True
    )

    # Calculate population density as specified in the lab
    gdf["pop_density"] = (
        gdf["pop_est"] / gdf.geometry.area
    )

    # Apply logarithmic transformation if selected
    if use_log_scale:
        gdf["pop_density"] = np.log1p(
            gdf["pop_density"]
        )

    fig, ax = plt.subplots(figsize=(12, 7))

    gdf.plot(
        column="pop_density",
        cmap=color_scheme,
        linewidth=0.5,
        edgecolor="black",
        legend=True,
        ax=ax
    )

    ax.set_title(
        "Population Density by Country",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_axis_off()

    st.pyplot(fig)
    plt.close(fig)


# --------------------------------------------------
# 7. GEO PROJECTION
# --------------------------------------------------

elif map_type == "Geo Projection":

    st.header("4. Geo Projection")

    st.write(
        "Explore how different geographical projections "
        "change the appearance of the world map."
    )

    # Define projection options
    projection_options = {
        "WGS 84 (EPSG:4326)": "EPSG:4326",
        "Web Mercator (EPSG:3857)": "EPSG:3857",
        "World Mercator (EPSG:3395)": "EPSG:3395",
        "World Equal Area (EPSG:6933)": "EPSG:6933"
    }

    # Select projection
    proj_choice = st.selectbox(
        "Select Map Projection:",
        list(projection_options.keys())
    )

    # Convert dataset to selected projection
    projected_gdf = gdf.to_crs(
        projection_options[proj_choice]
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    projected_gdf.plot(
        ax=ax,
        color="lightgreen",
        edgecolor="black",
        linewidth=0.5
    )

    ax.set_title(
        f"World Map - {proj_choice}",
        fontsize=15,
        fontweight="bold"
    )

    ax.set_axis_off()

    st.pyplot(fig)
    plt.close(fig)
