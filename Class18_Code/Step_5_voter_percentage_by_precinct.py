import geopandas as gpd
from matplotlib import pyplot as plt
from pathlib import Path


def main():
    data_path = Path("../Output")
    dem_gpkg_file = data_path / "dem_count_by_precinct.gpkg"
    rep_gpkg_file = data_path / "rep_count_by_precinct.gpkg"
    una_gpkg_file = data_path / "una_count_by_precinct.gpkg"

    dem_gdf = gpd.read_file(dem_gpkg_file, engine="pyogrio")
    rep_gdf = gpd.read_file(rep_gpkg_file, engine="pyogrio")
    una_gdf = gpd.read_file(una_gpkg_file, engine="pyogrio")

    total_voters_by_precinct = dem_gdf["Count"] + rep_gdf["Count"] + una_gdf["Count"]
    dem_per = 100 * dem_gdf["Count"] / total_voters_by_precinct
    rep_per = 100 * rep_gdf["Count"] / total_voters_by_precinct
    una_per = 100 * una_gdf["Count"] / total_voters_by_precinct

    dem_gdf.insert(len(dem_gdf.columns), column="Percent", value=dem_per)
    rep_gdf.insert(len(rep_gdf.columns), column="Percent", value=rep_per)
    una_gdf.insert(len(una_gdf.columns), column="Percent", value=una_per)

    fig, axes = plt.subplots(nrows=3, ncols=3)
    dem_gdf.plot(column="Count", ax=axes[0, 0], legend=True, cmap="jet")
    rep_gdf.plot(column="Count", ax=axes[1, 0], legend=True, cmap="jet")
    una_gdf.plot(column="Count", ax=axes[2, 0], legend=True, cmap="jet")
    
    dem_gdf.plot(column="Density", ax=axes[0, 1], legend=True, cmap="jet")
    rep_gdf.plot(column="Density", ax=axes[1, 1], legend=True, cmap="jet")
    una_gdf.plot(column="Density", ax=axes[2, 1], legend=True, cmap="jet")

    dem_gdf.plot(column="Percent", ax=axes[0, 2], legend=True, cmap="jet")
    rep_gdf.plot(column="Percent", ax=axes[1, 2], legend=True, cmap="jet")
    una_gdf.plot(column="Percent", ax=axes[2, 2], legend=True, cmap="jet")

    axes[0, 0].set_title("DEM Count")
    axes[1, 0].set_title("REP Count")
    axes[2, 0].set_title("UNA Count")

    axes[0, 1].set_title("DEM Density")
    axes[1, 1].set_title("REP Density")
    axes[2, 1].set_title("UNA Density")

    axes[0, 2].set_title("DEM Percentage")
    axes[1, 2].set_title("REP Percentage")
    axes[2, 2].set_title("UNA Percentage")

    plt.show()


if __name__ == "__main__":
    main()
