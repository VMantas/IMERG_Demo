import os
import streamlit as st
import earthaccess
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime, timedelta

# Set up page configuration
st.set_page_config(layout="wide")
st.title("GPM IMERG Precipitation Data Viewer")

# Authenticate with NASA EarthData
@st.cache_resource
def authenticate():
    # earthaccess will use environment variables EARTHDATA_USERNAME and EARTHDATA_PASSWORD if set
    auth = earthaccess.login()
    return auth

auth = authenticate()

# Retrieve GPM IMERG data
@st.cache_data
def get_gpm_imerg_data():
    yesterday = datetime.utcnow().date() - timedelta(days=1)
    data_date = yesterday.strftime("%Y%m%d")
    
    # Search for the GPM IMERG data
    results = earthaccess.search_data(
        short_name="GPM_3IMERGDF",
        cloud_hosted=True,
        temporal=(f"{data_date}", f"{data_date}"),
        bounding_box=(-180, -90, 180, 90)
    )
    
    if not results:
        st.error(f"No data found for {yesterday}")
        return None
    
    # Open the dataset using xarray
    ds = xr.open_dataset(results[0].data_links()[0], engine="h5netcdf")
    return ds

data = get_gpm_imerg_data()

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
def plot_precipitation(data, min_lon, max_lon, min_lat, max_lat, vmin, vmax):
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Plot the precipitation data
    im = data.precipitationCal.sel(lon=slice(min_lon, max_lon), lat=slice(min_lat, max_lat)).plot(
        ax=ax, transform=ccrs.PlateCarree(), cmap='viridis', 
        vmin=vmin, vmax=vmax, add_colorbar=False
    )
    
    # Add coastlines and gridlines
    ax.coastlines()
    ax.gridlines(draw_labels=True)
    
    # Add a colorbar
    cbar = fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.08, aspect=30)
    cbar.set_label('Precipitation (mm/day)')
    
    # Set the title
    ax.set_title(f"GPM IMERG Precipitation {data.time.dt.date.values[0]}")
    
    # Set the extent
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
    
    return fig

if data is not None:
    st.pyplot(plot_precipitation(data, min_lon, max_lon, min_lat, max_lat, vmin, vmax))
else:
    st.warning("No data available to display.")
