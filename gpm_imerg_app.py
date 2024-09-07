import streamlit as st

import os
import earthaccess
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime


# Set up page configuration
st.set_page_config(layout="wide")
st.title("GPM IMERG Precipitation Data Viewer")

# Authenticate with NASA EarthData
@st.cache_resource
def authenticate():
    auth = earthaccess.login()
    return auth

auth = authenticate()


# Retrieve GPM IMERG data
def get_gpm_imerg_data():
    # Set the date to December 28, 2020
    data_date = "20201228"

    # Search for the GPM IMERG Final data
    results = earthaccess.search_data(
        short_name="GPM_3IMERGDF",
        version="07",
        cloud_hosted=True,
        temporal=(f"{data_date}", f"{data_date}"),
        bounding_box=(-180, -90, 180, 90)
    )

    # Debugging: show results and check if data is returned
    st.write(f"Search results: {results}")

    if not results:
        st.error(f"No data found for {data_date}")
        return None

    try:
        # Get the first available dataset link
        dataset_link = results[0].data_links()[0]
        st.write(f"Dataset link: {dataset_link}")

        # Open the dataset using rasterio
        with rasterio.open(dataset_link) as src:
            # Get the precipitation data band (assuming band name is 'precipitationCal')
            precipitation = src.read(1)

            # Get the geo-transform and CRS for plotting
            transform = src.transform
            crs = src.crs

            return precipitation, transform, crs

    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        return None


# Load the data (no caching for now to avoid issues with file locking)
data, transform, crs = get_gpm_imerg_data()

# Add a sidebar for user inputs
st.sidebar.header("Settings")

# Region selection
min_lon = st.sidebar.slider("Min Longitude", -180, 180, -180)
max_lon = st.sidebar.slider("Max Longitude", -180, 180, 180)
min_lat = st.sidebar.slider("Min Latitude", -90, 90, -90)
max_lat = st.sidebar.slider("Max Latitude", -90, 90, 90)

# Color scale adjustment
vmin = st.sidebar.slider("Min Precipitation (mm/day)", 0, 50, 0)
vmax = st.sidebar.slider("Max Precipitation (mm/day)", 0, 200, 50)


# Create a map of precipitation data
def plot_precipitation(data, transform, crs, min_lon, max_lon, min_lat, max_lat, vmin, vmax):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Select the precipitation data within the specified region
    data_subset = data[:, min_lat:max_lat, min_lon:max_lon]

    # Plot the precipitation data using rasterio.plot.show
    show(
        data_subset,
        transform=transform,
        ax=ax,
        cmap='viridis',
        vmin=vmin,
        vmax=vmax,
        crs=crs,
    )

    # Add coastlines and gridlines
    ax.coastlines()
    ax.gridlines(draw_labels=True)

    # Add a colorbar
    cbar = fig.colorbar(ax=ax, orientation='horizontal', pad=0.08, aspect=30)
    cbar.set_label('Precipitation (mm/day)')

    # Set the title
    date_str = datetime.strptime(data.name, "%Y-%m-%d").strftime("%B %d, %Y")
    ax.set_title(f"GPM IMERG Final Precipitation {date_str}")
