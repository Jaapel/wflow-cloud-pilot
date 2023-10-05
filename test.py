import rioxarray
import xarray as xr

fn = "s3://hydromt-data/topography/merit_hydro/elv.vrt"
kwargs = {
    "masked": False,
    "default_name": "data",
    "engine": "rasterio",
    "mask_and_scale": False,
    "chunks": {"x": 6000, "y": 6000},
}
da = xr.open_dataarray(fn, **kwargs)
da
