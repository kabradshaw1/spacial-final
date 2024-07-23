import geopandas as gpd
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np

def count_voters_by_polygon(voters_gdf, polygons_gdf):
    # create result GeoDataFrame
    data = np.zeros((len(polygons_gdf), 2))
    result_gdf = gpd.GeoDataFrame(data=data,
                                  columns=("Count", "Density"),
                                  geometry=polygons_gdf.geometry)
    # Convert to appropriate CRS for area calculation
    polygon_2264 = polygons_gdf.to_crs("EPSG:2264")
    
    for i, polygon in polygons_gdf.iterrows():
        within_polygon = voters_gdf.within(polygon.geometry)
        count = within_polygon.sum()
        area = polygon_2264.loc[i].geometry.area * 3.86102e-7  # square miles
        density = count / area if area != 0 else 0
        result_gdf.at[i, "Count"] = count
        result_gdf.at[i, "Density"] = density

    return result_gdf

def plot_voter_distribution(voters_gdf, district_name, output_path):
    # Create the plot
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
    voters_gdf.plot(column="Count", ax=axes[0], cmap="jet", legend=True)
    voters_gdf.plot(column="Density", ax=axes[1], cmap="jet", legend=True)
    
    axes[0].set_title(f"{district_name} Voter Count")
    axes[1].set_title(f"{district_name} Voter Density")
    plt.suptitle(f"Pitt County Voter Distribution by {district_name} School Districts, by Kyle Bradshaw (email@example.com)")
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    
    plt.savefig(output_path, dpi=300)
    plt.close()

def main():
    code_path = Path(__file__).resolve().parent
    data_path = code_path.parent / "Data"
    figures_path = code_path.parent / "Figures"
    figures_path.mkdir(parents=True, exist_ok=True)

    # Load GIS and voter data
    elementary_school_gdf = gpd.read_file(data_path / "GIS_Data/Pitt_County_Elementary_School_Attendance_Districts/Pitt_County_Elementary_School_Attendance_Districts.shp")
    middle_school_gdf = gpd.read_file(data_path / "GIS_Data/Pitt_County_Middle_School_Attendance_Districts/Pitt_County_Middle_School_Attendance_Districts.shp")
    high_school_gdf = gpd.read_file(data_path / "GIS_Data/Pitt_County_High_School_Attendance_Districts/Pitt_County_High_School_Attendance_Districts.shp")
    voters_gdf = gpd.read_file(data_path / "pitt_voters.gpkg")

    # Ensure voters_gdf is in the same CRS as the school district data
    if voters_gdf.crs != "EPSG:2264":
        voters_gdf = voters_gdf.to_crs(epsg=2264)

    # Filter voters by party affiliation
    party_affiliations = ["DEM", "REP", "UNA"]
    for school_gdf, school_level in zip([elementary_school_gdf, middle_school_gdf, high_school_gdf],
                                        ["Elementary", "Middle", "High"]):
        for party in party_affiliations:
            party_voters_gdf = voters_gdf[voters_gdf["party_cd"] == party]
            voter_distribution_gdf = count_voters_by_polygon(party_voters_gdf, school_gdf)
            
            output_filename = figures_path / f"{school_level.lower()}_school_distribution_{party.lower()}_KyleBradshaw.jpg"
            plot_voter_distribution(voter_distribution_gdf, school_level, output_filename)

if __name__ == "__main__":
    main()
