import numpy as np
import os
import sys
import argparse


def tlm_fit_thermalexpansion(my_data):
    expcoefs = my_data["expcoefs"]
    rmses = my_data["rmses"]
    expcoefs_models = my_data["expcoefs_models"]
    rmses_models = my_data["rmses_models"]

    # Cumulative probability at which to trim the distribution of models
    pb_clip = 0.85

    # Clip gsat rmse cdf
    rmses_sorted = np.sort(rmses)
    sort_idx = np.argsort(rmses)
    pbs = np.arange(0, rmses_sorted.size) / rmses_sorted.size

    # Find which models to cut out
    include_models = rmses_models[sort_idx][pbs <= pb_clip]

    # Extract the coefficients for the models that made the cut
    model_idx = np.isin(expcoefs_models, include_models)
    expcoefs_clipped = expcoefs[model_idx]

    # Extract normal distribution modes
    mean_expcoefs = np.mean(expcoefs_clipped)
    std_expcoefs = np.std(expcoefs_clipped)

    # Store preprocessed data in pickles
    output = {
        "mean_expcoefs": mean_expcoefs,
        "std_expcoefs": std_expcoefs,
        "include_models": include_models,
        "pb_clip": pb_clip,
    }
    return output


if __name__ == "__main__":
    # Initialize the command-line argument parser
    parser = argparse.ArgumentParser(
        description="Run the fitting stage for the TLM ocean dynamics workflow",
        epilog="Note: This is meant to be run as part of the Framework for the Assessment of Changes To Sea-level (FACTS)",
    )

    # Define the command line arguments to be expected
    parser.add_argument(
        "--pipeline_id", help="Unique identifier for this instance of the module"
    )

    # Parse the arguments
    args = parser.parse_args()

    # Define the names of the intermediate files this run will generate
    outdir = os.path.dirname(__file__)
    tlmfitfile = os.path.join(outdir, "{}_tlmfit.pkl".format(args.pipeline_id))

    # Runs the TLM fitting stage if intermediate files are not present
    if os.path.isfile(tlmfitfile):
        print("{} found, skipping TE fitting".format(tlmfitfile))
    else:
        tlm_fit_thermalexpansion(args.pipeline_id)

    # Done
    sys.exit()
