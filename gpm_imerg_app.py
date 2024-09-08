import streamlit as st
import os
import earthaccess
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime


st.write("Available netCDF engines:", xr.backends.list_engines())

# Set up page configuration
st.set_page_config(layout="wide")
st.title("GPM IMERG Precipitation Data Viewer")

# Authenticate with NASA EarthData
@st.cache_resource
def authenticate():
    auth = earthaccess.login()
    return auth

auth = authenticate()

def get_gpm_imerg_data():
    data_date = "20201228"
    
    results = earthaccess.search_data(
        short_name="GPM_3IMERGDF",
        version="07",
        cloud_hosted=True,
        temporal=(f"{data_date}", f"{data_date}"),
        bounding_box=(-180, -90, 180, 90)
    )
    
    st.write(f"Search results: {results}")
    
    if not results:
        st.error(f"No data found for {data_date}")
        return None
    
    try:
        dataset_link = results[0].data_links()[0]
        st.write(f"Dataset link: {dataset_link}")
        
        # Try different engines
        for engine in ['netcdf4', 'h5netcdf']:
            try:
                ds = xr.open_dataset(dataset_link, engine=engine)
                st.success(f"Successfully opened dataset with {engine} engine")
                return ds
            except Exception as e:
                st.write(f"Failed to open with {engine} engine: {str(e)}")
        
        st.error("Failed to open dataset with any available engine")
        return None
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        return None

# Load the data (no caching for now to avoid issues with file locking)
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
    ax.set_title(f"GPM IMERG Final Precipitation {data.time.dt.date.values[0]}")
    
    # Set the extent
    ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
    
    return fig

# Check if data is available before plotting
if data is not None:
    st.pyplot(plot_precipitation(data, min_lon, max_lon, min_lat, max_lat, vmin, vmax))
else:
    st.warning("No data available to display.")
