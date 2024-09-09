import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

# Set up Streamlit page
st.title("GPM IMERG Final Precipitation Data")

# Upload NetCDF file
uploaded_file = st.file_uploader("Upload GPM IMERG Final NetCDF File", type="nc")

if uploaded_file:
    # Open the NetCDF file
    nc = Dataset(uploaded_file, mode='r')

    # Display available variables
    st.subheader("Available Variables:")
    variables = list(nc.variables.keys())
    st.write(variables)

    # Select precipitation variable (Assuming it’s named "precipitation" in the dataset)
    precip_var = st.selectbox("Select Precipitation Variable", variables)

    if precip_var:
        # Extract the precipitation data
        precip_data = nc.variables[precip_var][:]

        # Select a time slice for visualization
        time_dim = nc.variables['time'][:]
        time_index = st.slider("Select Time Index", 0, len(time_dim)-1, 0)

        # Select a geographic region to display
        lat = nc.variables['lat'][:]
        lon = nc.variables['lon'][:]
        lat_range = st.slider("Latitude Range", float(lat.min()), float(lat.max()), (lat.min(), lat.max()))
        lon_range = st.slider("Longitude Range", float(lon.min()), float(lon.max()), (lon.min(), lon.max()))

        # Filter data by selected region
        lat_filter = np.where((lat >= lat_range[0]) & (lat <= lat_range[1]))[0]
        lon_filter = np.where((lon >= lon_range[0]) & (lon <= lon_range[1]))[0]
        selected_precip_data = precip_data[time_index, lat_filter, :][:, lon_filter]

        # Plot the data
        st.subheader("Precipitation Data Visualization")
        fig, ax = plt.subplots()
        im = ax.imshow(selected_precip_data, cmap='Blues', aspect='auto', origin='lower')
        plt.colorbar(im, ax=ax, label="mm/h")
        st.pyplot(fig)

    # Close the NetCDF file
    nc.close()

