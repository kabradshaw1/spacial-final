import geopandas as gpd
from pathlib import Path
from matplotlib import pyplot as plt

# read the geopackage file
print("read data")
data_path = Path("../Output")
all_voters_gpkg_file = data_path / "all_voters_method_1.gpkg"
all_voters_gdf = gpd.read_file(all_voters_gpkg_file, engine="pyogrio")

# subset the voters according to party group
print("subset data by party group")
dem_voters = all_voters_gdf[all_voters_gdf["party_cd"] == "DEM"]
rep_voters = all_voters_gdf[all_voters_gdf["party_cd"] == "REP"]
una_voters = all_voters_gdf[all_voters_gdf["party_cd"] == "UNA"]

# save the data
print("save data into files")
dem_gpkg_file = data_path / "dem_voters.gpkg"
dem_voters.to_file(dem_gpkg_file, driver="GPKG", engine="pyogrio")

rep_gpkg_file = data_path / "rep_voters.gpkg"
rep_voters.to_file(rep_gpkg_file, driver="GPKG", engine="pyogrio")

una_gpkg_file = data_path / "una_voters.gpkg"
una_voters.to_file(una_gpkg_file, driver="GPKG", engine="pyogrio")

fig1, ax1 = plt.subplots(nrows=1, ncols=1)
dem_voters.plot(ax=ax1, markersize=0.5)
ax1.set_title("Democratic Voters")
fig1.savefig("../Figures/dem_voters.jpg", dpi=300)

fig2, ax2 = plt.subplots(nrows=1, ncols=1)
rep_voters.plot(ax=ax2, markersize=0.5)
ax2.set_title("Republican Voters")

fig3, ax3 = plt.subplots(nrows=1, ncols=1)
una_voters.plot(ax=ax3, markersize=0.5)
ax3.set_title("Unaffiliated Voters")
plt.show()



