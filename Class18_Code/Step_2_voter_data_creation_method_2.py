import pandas as pd
import geopandas as gpd
from pathlib import Path

data_path = Path("../Data")
csv_file = data_path / "pitt_count_final_geocoding_results.csv"
# read the csv file
csv_data = pd.read_csv(csv_file)
print(csv_data.columns)

# subset the data according to LAT/LON values, -9999 indicating unsuccessful geocoding
selection_flags = csv_data["LAT"] != -9999
geocoded_csv = csv_data[selection_flags]
print("There are %d rows in csv_data and %d rows in geocoded_csv" % (csv_data.shape[0], geocoded_csv.shape[0]))

# geocoded_csv inherited the index of csv_data. Let's reindex it.
geocoded_csv = geocoded_csv.reset_index()

# Generate GeometryArray of shapely Point geometries from x, y(, z) coordinates
address_points = gpd.points_from_xy(geocoded_csv["LON"], geocoded_csv["LAT"], crs="EPSG:4326")

# add a geometry column to the geocoded_csv file
geocoded_csv["geometry"] = address_points

# create a GeoDataFrame
gdf = gpd.GeoDataFrame(data=geocoded_csv, geometry=geocoded_csv["geometry"], crs="EPSG:4326")

# save the GeoDataFrame
output_folder = Path("../Output")
gpkg_file = output_folder / "all_voters_method_2.gpkg"
gdf.to_file(gpkg_file, driver="GPKG")
