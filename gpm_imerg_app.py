import streamlit as st
import os
import earthaccess
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime

# Set up page configuration
st.set_page_config(layout="wide")
st.title("GPM IMERG Precipitation Data Viewer")

# Authenticate with NASA EarthData
@st.cache_resource
def authenticate():
    try:
        auth = earthaccess.login()
        st.success("Successfully authenticated with NASA EarthData")
        return auth
    except Exception as e:
        st.error(f"Authentication failed: {str(e)}")
        return None

auth = authenticate()

# Retrieve GPM IMERG data
def get_gpm_imerg_data():
    data_date = "20201228"
    
    try:
        results = earthaccess.search_data(
            short_name="GPM_3IMERGDF",
            version="07",
            cloud_hosted=False,
            temporal=(f"{data_date}", f"{data_date}"),
            bounding_box=(-180, -90, 180, 90)
        )
        
        st.write(f"Number of results found: {len(results)}")
        
        if not results:
            st.error(f"No data found for {data_date}")
            return None
        
        dataset_link = results[0].data_links()[0]
        st.write(f"Dataset link: {dataset_link}")
        
        # Open dataset with chunking to reduce memory usage
        chunks = {'lon': 10, 'lat': 10, 'time': 1}
        with xr.open_dataset('https://data.gesdisc.earthdata.nasa.gov/data/GPM_L3/GPM_3IMERGDF.07/2020/12/3B-DAY.MS.MRG.3IMERG.20201228-S000000-E235959.V07B.nc4', engine='netCDF4', chunks=chunks) as ds:
            # Load only the precipitation data
            precip_data = ds['precipitationCal'].load()
        
        st.success("Successfully loaded precipitation data")
        return precip_data
    except Exception as e:
        st.error(f"Error in get_gpm_imerg_data: {str(e)}")
        return None

# Load the data (without caching)
st.write("Attempting to load GPM IMERG data...")
data = get_gpm_imerg_data()

if data is not None:
    st.success("Data loaded successfully")
    st.write("Data shape:", data.shape)
else:
    st.error("Failed to load data")

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
    try:
        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        
        # Plot the precipitation data
        im = data.sel(lon=slice(min_lon, max_lon), lat=slice(min_lat, max_lat)).plot(
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
        ax.set_title(f"GPM IMERG Final Precipitation {data.time.values[0]}")
        
        # Set the extent
        ax.set_extent([min_lon, max_lon, min_lat, max_lat], crs=ccrs.PlateCarree())
        
        return fig
    except Exception as e:
        st.error(f"Error in plot_precipitation: {str(e)}")
        return None

# Check if data is available before plotting
if data is not None:
    st.write("Attempting to create plot...")
    fig = plot_precipitation(data, min_lon, max_lon, min_lat, max_lat, vmin, vmax)
    if fig is not None:
        st.pyplot(fig)
    else:
        st.error("Failed to create plot")
else:
    st.warning("No data available to display.")
