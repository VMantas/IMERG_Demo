import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import tempfile
import cartopy.crs as ccrs  # For map projections
import cartopy.feature as cfeature  # For country borders

# Set up Streamlit page
st.title("GPM IMERG Final Precipitation Data with Geographic Boundaries")

# Upload NetCDF file
uploaded_file = st.file_uploader("Upload GPM IMERG Final NetCDF File", type="nc4")

if uploaded_file:
    try:
        # Save the uploaded file to a temporary file on disk
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        # Open the NetCDF file from the temporary file path
        nc = Dataset(tmp_file_path, mode='r')

        # Display the variables
        st.subheader("Available Variables:")
        variables = list(nc.variables.keys())
        st.write(variables)

        # Assume that the precipitation variable is present and use the first one for simplicity
        first_variable = variables[0]
        st.write(f"Displaying data for variable: {first_variable}")

        # Load the data from the selected variable
        data = nc.variables[first_variable][:]
        lat = nc.variables['lat'][:]  # Assuming the variable for latitude is 'lat'
        lon = nc.variables['lon'][:]  # Assuming the variable for longitude is 'lon'

        st.write("Data shape:", data.shape)

        # Set up the map plot with Cartopy
        fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})

        # Plot the data, flip or rotate if necessary
        if data.ndim == 3:
            im = ax.imshow(np.flipud(data[0, :, :]), extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                           transform=ccrs.PlateCarree(), cmap='Blues', origin='upper')
        elif data.ndim == 2:
            im = ax.imshow(np.flipud(data), extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                           transform=ccrs.PlateCarree(), cmap='Blues', origin='upper')


