import os
import geopandas as gpd
import pandas as pd
from pathlib import Path

# Set your folder and output
def mergeInner():
    checkMerged = Path(__file__).parent.resolve()/"merged"
    if  not checkMerged.exists():
        print("Creating folder 'merged'")
        os.mkdir(Path(__file__).parent.resolve()/"merged")
    for folder in os.listdir(Path(__file__).parent.resolve()):
        if folder =="merged":
            continue
        if folder =="__pycache__":
            continue
        check = Path(__file__).parent.resolve()/folder
        if not check.is_dir():
            continue
        cwd = Path(__file__).parent.resolve()/folder
        input_folder = cwd/"robert_accessability_muni_delivery"/"python"/"processed"/"Shapes"
        output_file = cwd.parent/"merged"/f"{folder} - merged.shp"
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

def mergeOuter():

    folder = Path(__file__).parent.resolve()/"merged"
    shapefiles = list(folder.glob("*.shp"))
    gdfs = []
    for shp in shapefiles:
        gdf = gpd.read_file(shp)
        gdf["source_file"] = shp.name  # optional: track which file it came from
        gdfs.append(gdf)

        
# check CRS consistency
    crs_set = {gdf.crs for gdf in gdfs}
    if len(crs_set) > 1:
        target_crs = gdfs[0].crs
        gdfs = [gdf.to_crs(target_crs) for gdf in gdfs]

    merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
    merged_gdf.to_file(folder/"merged_map.shp")
