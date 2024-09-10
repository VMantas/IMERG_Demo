import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import tempfile
import cartopy.crs as ccrs  # For map projections
import cartopy.feature as cfeature  # For country borders
import earthaccess  # For NASA EarthData authentication and download

# Set up Streamlit page
st.title("Test")

# Step 1: Authenticate with EarthData
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

# Step 2: Search and download GPM IMERG Final data from EarthData
def search_and_download_imer_data(date="20201228"):
    try:
        results = earthaccess.search_data(
            short_name="GPM_3IMERGDF",
            version="07",
            cloud_hosted=False,
            temporal=(f"{date}", f"{date}"),
            bounding_box=(-180, -90, 180, 90)
        )
        st.write(f"Number of results found: {len(results)}")
        
        if not results:
            st.error(f"No data found for {date}")
            return None
        
        # Get the first dataset
        dataset = results[0]
        dataset_link = dataset.data_links()[0]
        st.write(f"Dataset link: {dataset_link}")
        
        # Use earthaccess.download to handle authentication and download
        st.write("Attempting to download the dataset...")
        
        # Specify a temporary local path to save the file
        local_path = tempfile.gettempdir() + "/gpm_imerg_data.nc4"
        
        earthaccess.download(dataset, local_path=local_path)
        st.success(f"Successfully downloaded the data to {local_path}")
        
        return local_path
    except Exception as e:
        st.error(f"Error in search_and_download_imer_data: {str(e)}")
        return None

# Step 3: Load the data from NASA EarthData
data_file = search_and_download_imer_data()

if data_file:
    try:
        # Open the NetCDF file from the downloaded file path
        st.write(f"Downloaded file link: {data_file}")
        st.download_button(label="Download NC4 File", data=open(data_file, 'r'), file_name="gpm_imerg_data.nc4", mime="application/x-netcdf4")
        nc = Dataset(data_file, mode='r')  # Use the correct local_path here
        

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

        # Step 4: Set up the map plot with Cartopy
        fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})

        # Plot the data, flip or rotate if necessary
        if data.ndim == 3:
            im = ax.imshow(np.flipud(data[0, :, :]), extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                           transform=ccrs.PlateCarree(), cmap='Blues', origin='upper', vmin=0, vmax=50)
        elif data.ndim == 2:
            im = ax.imshow(np.flipud(data), extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                           transform=ccrs.PlateCarree(), cmap='Blues', origin='upper')

        # Add a colorbar
        cbar = fig.colorbar(im, ax=ax, orientation='vertical', pad=0.05)
        cbar.set_label("Precipitation (mm/h)")

        # Add country borders and coastlines
        ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black')
        ax.add_feature(cfeature.COASTLINE, linewidth=1)

        # Add gridlines for better readability
        ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

        # Display the plot
        st.pyplot(fig)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

    finally:
        # Safely close the NetCDF file
        try:
            nc.close()
        except Exception as e:
            st.error(f"An error occurred while closing the NetCDF file: {e}")
