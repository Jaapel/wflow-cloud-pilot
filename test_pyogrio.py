import geopandas
from geopandas import read_file
from hydromt.gis_utils import parse_geom_bbox_buffer
from pyogrio import read_dataframe

crs = 4326
bbox = (9.566, 0.3476, 9.766, 0.5476)
geom = parse_geom_bbox_buffer(geom=None, bbox=bbox, buffer=0)

geopandas.options.io_engine = "pyogrio"

if __name__ == "__main__":
    df = read_dataframe(
        "s3://hydromt-data/topography/merit_hydro/basin_index.fgb",
        bbox=bbox,
        geom=geom,
        crs=crs,
    )

    print(df.__repr__())

    df = read_file(
        "s3://hydromt-data/topography/merit_hydro/basin_index.fgb",
        bbox=bbox,
        geom=geom,
        crs=crs,
    )

    print(df.__repr__())
