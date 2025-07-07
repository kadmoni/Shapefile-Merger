import os
import geopandas as gpd
import pandas as pd

# Set your folder and output
input_folder = "C:\\Users\\User\\Desktop\\DEV\\Shapefile-merger\\shapes"
output_file = "C:\\Users\\User\\Desktop\\DEV\\Shapefile-merger\\merged\\merged.shp"

# Find all .shp files in the folder
shapefiles = [f for f in os.listdir(input_folder) if f.endswith(".shp")]

merged_df = None
geometry = None

for shp_file in shapefiles:
    path = os.path.join(input_folder, shp_file)
    gdf = gpd.read_file(path)

    # Check for required 'o_id' field
    if 'o_id' not in gdf.columns:
        raise ValueError(f"'o_id' field missing in {shp_file}")

    # Save geometry from the first file
    if geometry is None:
        geometry = gdf.set_index('o_id').geometry

    # Drop geometry, keep all data columns except o_id and geometry
    data_cols = [col for col in gdf.columns if col not in ['o_id', 'geometry']]

    # Prefix data columns with file name
    prefix = os.path.splitext(shp_file)[0].split("_")[2]
    gdf_renamed = gdf[['o_id'] + data_cols].copy()
    gdf_renamed = gdf_renamed.rename(columns={col: f"{prefix}_{col}" for col in data_cols})

    # Merge into main DataFrame
    if merged_df is None:
        merged_df = gdf_renamed
    else:
        merged_df = pd.merge(merged_df, gdf_renamed, on='o_id', how='outer')

# Reattach geometry
final_gdf = gpd.GeoDataFrame(merged_df.set_index('o_id'), geometry=geometry)
final_gdf = final_gdf.reset_index()  # restore 'o_id' as column

# Save the merged file
final_gdf.to_file(output_file)

print(f"Merged shapefile saved to: {output_file}")
