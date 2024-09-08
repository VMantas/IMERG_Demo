import streamlit as st
import earthaccess
import xarray as xr
import os
import requests

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
        
        # Download the NetCDF4 file locally
        response = requests.get(dataset_link)
        file_name = "data.nc4"
        
        with open(file_name, 'wb') as f:
            f.write(response.content)
        
        # Open the downloaded dataset with chunking to reduce memory usage
        chunks = {'lon': 10, 'lat': 10, 'time': 1}
        with xr.open_dataset(file_name, chunks=chunks) as ds:
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

