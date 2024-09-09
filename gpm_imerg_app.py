import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import tempfile

# Set up Streamlit page
st.title("GPM IMERG Final Precipitation Data")

# Upload NetCDF file
uploaded_file = st.file_uploader("Upload GPM IMERG Final NetCDF File", type="nc")

if uploaded_file:
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
    st.write("Data shape:", data.shape)

    # Plot the data for the first time slice and first spatial slice (if multidimensional)
    fig, ax = plt.subplots()
    if data.ndim == 3:
        ax.imshow(data[0, :, :], cmap='Blues', origin='lower')
    elif data.ndim == 2:
        ax.imshow(data, cmap='Blues', origin='lower')
    plt.colorbar(ax.imshow(data[0, :, :], cmap='Blues', origin='lower'))
    st.pyplot(fig)

    # Close the NetCDF file
    nc.close()
