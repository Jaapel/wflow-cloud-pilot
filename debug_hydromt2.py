import geopandas as gpd
from hydromt.data_adapter import GeoDataFrameAdapter
from shapely import box

fn = "s3://hydromt-data/hydrography/reservoirs/reservoir-db.fgb"
geom = (9.654999999999973, 0.3475000000002808, 9.861666666666451, 0.4866666666668209)
if __name__ == "__main__":
    da = GeoDataFrameAdapter(path=fn, driver="vector")
    gdf = da.get_data(bbox=None, geom=gpd.GeoSeries(box(*geom)).set_crs(epsg=4326))
    gdf
