from pathlib import Path
import geopandas as gpd

"""
    Goals:
        (1) Convert Shapefile into GeoPackage 
        (2) Convert CRS into EPSG:4326 
"""
GIS_data_folder = Path("../Pitt_County_GIS_Data")
shape_file_dict = {
    "precinct": "Pitt_County_Precincts/Pitt_County_Precincts.shp",
    "middle_school_district": "Pitt_County_Middle_School_Attendance_Districts/Pitt_County_Middle_School_Attendance_Districts.shp",
    "education_board_district": "Pitt_County_Board_of_Education_Districts/Pitt_County_Board_of_Education_Districts.shp",
    "high_school_district": "Pitt_County_High_School_Attendance_Districts/Pitt_County_High_School_Attendance_Districts.shp",
    "elementary_school_district": "Pitt_County_Elementary_School_Attendance_Districts/Pitt_County_Elementary_School_Attendance_Districts.shp",
    "pitt_city": "./Pitt_County_City_Limits/Pitt_County_City_Limits.shp"
}

output_folder = Path("../Output")

for dataset_name, dataset_path in shape_file_dict.items():
    shape_file = GIS_data_folder / dataset_path
    gdf = gpd.read_file(shape_file)
    print(shape_file, " original CRS: ", gdf.crs)
    gdf.to_crs("EPSG:4326", inplace=True)     # GPS format
    gpkg_file = output_folder / ("%s.gpkg" % dataset_name)
    gdf.to_file(gpkg_file, driver="GPKG", engine="pyogrio")

