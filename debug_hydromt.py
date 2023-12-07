import json
import logging
from os.path import join

import numpy as np
from boto3 import Session
from hydromt import log
from hydromt.cli import cli_utils
from hydromt.models import MODELS

# s3_client = Session().client("s3")
# buckets = s3_client.list_buckets()

model = "wflow"
opt = None
model_root = "./wflow_small"
region = json.loads('{"subbasin": [9.666, 0.4476], "uparea": 100}')
config = "wflow-build.ini"
data = ["data_catalogs/deltares-data-curated-minio.yaml"]
verbose = 2
dd = False
fo = True
cache = False
quiet = 0

logger = logging.getLogger(__name__)


def build(
    model,
    model_root,
    opt,
    config,
    region,
    data,
    dd,
    fo,
    cache,
    verbose,
    quiet,
):
    """Build models from scratch.

    Example usage:
    --------------

    To build a wflow model for a subbasin using a point coordinates snapped to cells
    with upstream area >= 50 km2
    hydromt build wflow /path/to/model_root -i /path/to/wflow_config.ini  -r "{'subbasin': [-7.24, 62.09], 'uparea': 50}" -d deltares_data -d /path/to/data_catalog.yml -v

    To build a sfincs model based on a bbox
    hydromt build sfincs /path/to/model_root  -i /path/to/sfincs_config.ini  -r "{'bbox': [4.6891,52.9750,4.9576,53.1994]}"  -d /path/to/data_catalog.yml -v

    """  # noqa: E501
    log_level = max(10, 30 - 10 * (verbose - quiet))
    logger = log.setuplog(
        "build", join(model_root, "hydromt.log"), log_level=log_level, append=False
    )
    logger.info(f"Building instance of {model} model at {model_root}.")
    logger.info("User settings:")
    opt = cli_utils.parse_config(config, opt_cli=opt)
    kwargs = opt.pop("global", {})
    # Set region to None if empty string json
    if len(region) == 0:
        region = None
    # parse data catalog options from global section in config and cli options
    data_libs = np.atleast_1d(kwargs.pop("data_libs", [])).tolist()  # from global
    data_libs += list(data)  # add data catalogs from cli
    if dd and "deltares_data" not in data_libs:  # deltares_data from cli
        data_libs = ["deltares_data"] + data_libs  # prepend!
    try:
        # initialize model and create folder structure
        mode = "w+" if fo else "w"
        mod = MODELS.load(model)(
            root=model_root,
            mode=mode,
            logger=logger,
            data_libs=data_libs,
            **kwargs,
        )
        mod.data_catalog.cache = cache
        # build model
        mod.build(region, opt=opt)
    except Exception as e:
        logger.exception(e)  # catch and log errors
        raise
    finally:
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


if __name__ == "__main__":
    build(
        model,
        model_root,
        opt,
        config,
        region,
        data,
        dd,
        fo,
        cache,
        verbose,
        quiet,
    )
