from hydromt.gis_utils import parse_geom_bbox_buffer
from hydromt.io import open_vector
from upath.implementations.cloud import S3Path

path = S3Path(
    "s3://hydromt-data/topography/merit_hydro/basin_index.fgb",
)
crs = 4326
bbox = [9.566, 0.3476, 9.766, 0.5476]
geom = parse_geom_bbox_buffer(geom=None, bbox=bbox, buffer=0)

if __name__ == "__main__":
    open_vector(path, bbox=bbox, geom=geom, crs=crs)
