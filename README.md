# Cloud Pilot

Working repo for the HydroMT cloud pilot.

Current steps to get things working:
1. create environment by `mamba env create -f environment.yaml`
1. install latest hydromt version using `pip install git+https://github.com/deltares/hydromt.git`
1. install latest hydromt_wflow version with patches `git+https://github.com/deltares/hydromt_wflow.git@implement_nodata`
1. enter temporary credentials in `.env` (see example in `.<aws-env>.env.example`)
1. upload data using `utils/push_data_create_catalog.py`
To be tested:
1. run wflow and check data usage using `./monitor.sh`
1. analyse output with `notebooks/plot_results.ipynb`