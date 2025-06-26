import numpy as np
import time
import argparse
from scipy.stats import norm
from scipy.stats import t

import xarray as xr


""" tlm_postprocess_oceandynamics.py

This runs the post-processing stage for the ocean dynamics component of the TLM
workflow. Projections generated from this stage are site-specific and include both the
ocean dynamics and thermal expansion contributions.

Parameters:
nsamps = Number of samples to draw
rng_seed = Seed value for the random number generator
pipeline_id = Unique identifier for the pipeline running this code

Note that the value of 'nsamps' and 'rng_seed' are shared between the projection stage
and the post-processing stage when run within FACTS.

"""


def tlm_postprocess_oceandynamics(
    my_config,
    my_zos,
    my_od_fit,
    my_te_projections,
    nsamps,
    rng_seed,
    chunksize,
    output_lslr_file,
):
    # Extract the relevant data
    targyears = my_config["targyears"]
    scenario = my_config["scenario"]
    baseyear = my_config["baseyear"]
    GCMprobscale = my_config["GCMprobscale"]
    no_correlation = my_config["no_correlation"]

    # Read in the TE projections data file ------------------------
    te_samps = xr.DataArray(
        my_te_projections["thermsamps"],
        dims=("samples", "years"),
        coords=(np.arange(nsamps), targyears),
    )

    # Evenly sample quantile space and permutate
    quantile_samps = np.linspace(0, 1, nsamps + 2)[1 : (nsamps + 1)]
    rng = np.random.default_rng(rng_seed)
    quantile_samps = rng.permutation(quantile_samps)
    q = xr.DataArray(quantile_samps, dims=["samples"], coords=[np.arange(nsamps)])

    # Determine the thermal expansion scale coefficient
    ThermExpScale = norm.ppf(0.95) / norm.ppf(GCMprobscale)

    # Note the selection and chunking at the end. This is selecting target
    # years only, must match years in thermal expansion samples data.
    # Chunking turns the databackend to dask arrays to handle
    # larger-than-memory data.
    od_fit = (
        xr.Dataset(
            {
                "od_mean": (("years", "locations"), my_od_fit["OceanDynMean"]),
                "od_std": (("years", "locations"), my_od_fit["OceanDynStd"]),
                "od_tecorr": (("years", "locations"), my_od_fit["OceanDynTECorr"]),
                "od_dof": (("years", "locations"), my_od_fit["OceanDynDOF"]),
                "lat": (["locations"], my_zos["focus_site_lats"]),
                "lon": (["locations"], my_zos["focus_site_lons"]),
            },
            coords={
                "years": my_od_fit["OceanDynYears"],
                "locations": my_zos["focus_site_ids"],
            },
        )
        .sel(years=targyears)
        .chunk({"locations": chunksize})
    )

    # Calculate the conditional mean and std dev if correlation is needed
    if no_correlation:
        condmean = od_fit["od_mean"]
        condstd = ThermExpScale * od_fit["od_std"]
    else:
        condmean = od_fit["od_mean"] + od_fit["od_std"] * od_fit["od_tecorr"] * (
            (te_samps - te_samps.mean(dim="samples")) / te_samps.std(dim="samples")
        )
        condstd = (
            ThermExpScale * od_fit["od_std"] * np.sqrt(1 - od_fit["od_tecorr"] ** 2)
        )

    # Use `t.ppf()' to get ocean dynamic samples but it needs to work on
    # chunked, dask-backed xarray Datasets/Arrays because the data we're
    # working with is potentially larger than memory.
    # We apply `constd` and `condmean` directly rather than use t.ppf()'s
    # "loc" and "scale" args because this appears to scale and handle
    # multiple chunked dimensions a bit more easily.
    od_samps = (
        xr.apply_ufunc(
            lambda q, dof: t.ppf(q, dof),
            q,
            od_fit["od_dof"],
            vectorize=True,
            input_core_dims=[["samples"], []],
            output_core_dims=[["samples"]],
            dask="parallelized",
            output_dtypes=[float],
        )
        * condstd
        + condmean
    )

    samps = od_samps + te_samps

    samps.name = "sea_level_change"
    samps.attrs = {"units": "mm"}
    samps = samps.to_dataset()
    samps.attrs = {
        "description": "Local SLR contributions from thermal expansion and dynamic sea-level according to Kopp 2014 CMIP6/TLM workflow",
        "history": "Created " + time.ctime(time.time()),
        "source": "SLR Framework: Kopp 2014 CMIP6/TLM workflow",
        "scenario": scenario,
        "baseyear": baseyear,
    }
    # ∵ lat and lon were variables, not coords, in original code.
    samps["lat"] = od_fit["lat"]
    samps["lon"] = od_fit["lon"]

    # Casting down to float32 because this data can be very large.
    # Casting float64 -> float32 reduces size by half and don't need
    # extra precision anyways.
    samps = samps.astype("float32")

    samps.to_netcdf(output_lslr_file)


if __name__ == "__main__":
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Run the post-processing stage for the TLM ocean dynamics workflow",
        epilog="Note: This is meant to be run as part of the Framework for the Assessment of Changes To Sea-level (FACTS)",
    )

    # Define the command line arguments to be expected
    parser.add_argument(
        "--nsamps", help="Number of samples to generate", default=20000, type=int
    )
    parser.add_argument(
        "--seed", help="Seed value for random number generator", default=1234, type=int
    )
    parser.add_argument(
        "--chunksize",
        help="Number of locations to process at a time [default=50]",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--keep_temp",
        help="Keep the temporary files? 1 = keep, 0 = remove [default=0]",
        type=int,
        default=0,
    )
    parser.add_argument(
        "--pipeline_id", help="Unique identifier for this instance of the module"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Run the postprocessing stage
    tlm_postprocess_oceandynamics(
        args.nsamps, args.seed, args.chunksize, args.keep_temp, args.pipeline_id
    )

    # Done
    exit()
