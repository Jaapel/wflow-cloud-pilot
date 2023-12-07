import geopandas as gpd
from hydromt import DataCatalog
from shapely import box

# fn = "s3://hydromt-data/hydrography/reservoirs/reservoir-db.fgb"
fn = "s3://hydro-mt-data/meto/era5_daily.zarr"
geom = gpd.GeoSeries(
    box(9.654999999999973, 0.3475000000002808, 9.861666666666451, 0.4866666666668209),
    crs=4326,
)
data_catalog_path = "data_catalogs/deltares-data-curated-minio.yaml"
starttime = "2010-01-01T00:00:00"
endtime = "2010-03-31T00:00:00"
# rename = {
#     "d2m": "temp_dew",
#     "msl": "press_msl",
#     "ssrd": "kin",
#     "t2m": "temp",
#     "tisr": "kout",
#     "tmax": "temp_max",
#     "tmin": "temp_min",
#     "tp": "precip",
#     "u10": "wind10_u",
#     "v10": "wind10_v",
# }
# unit_add = {
#     " "
# }
if __name__ == "__main__":
    data_catalog = DataCatalog(data_catalog_path)
    precip = data_catalog.get_rasterdataset(
        "era5",
        geom=geom,
        buffer=2,
        time_tuple=(starttime, endtime),
        variables=["precip"],
    )
    # da = RasterDatasetAdapter(fn, "zarr", "s3", 4326, rename=rename, unit_add=unit_add)
    # da = GeoDataFrameAdapter(
    #     path=fn, driver="vector", driver_kwargs={"engine": "pyogrio"}
    # )
    # gdf = da.get_data(bbox=None, geom=gpd.GeoSeries(box(*geom)).set_crs(epsg=4326))
    # gdf
