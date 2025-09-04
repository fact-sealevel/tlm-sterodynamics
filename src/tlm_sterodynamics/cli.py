"""
Logic for the CLI.
"""

import logging

import click

from tlm_sterodynamics.tlm_sterodynamics_preprocess_thermalexpansion import (
    tlm_preprocess_thermalexpansion,
)
from tlm_sterodynamics.tlm_sterodynamics_fit_thermalexpansion import (
    tlm_fit_thermalexpansion,
)
from tlm_sterodynamics.tlm_sterodynamics_project import tlm_project_thermalexpansion
from tlm_sterodynamics.tlm_sterodynamics_preprocess_oceandynamics import (
    tlm_preprocess_oceandynamics,
)
from tlm_sterodynamics.tlm_sterodynamics_fit_oceandynamics import tlm_fit_oceandynamics
from tlm_sterodynamics.tlm_sterodynamics_postprocess import (
    tlm_postprocess_oceandynamics,
)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@click.command
@click.option(
    "--pipeline-id",
    envvar="TLM_STERODYNAMICS_PIPELINE_ID",
    help="Unique identifier for this instance of the module.",
    required=True,
)
@click.option(
    "--output-gslr-file",
    envvar="TLM_STERODYNAMICS_OUTPUT_GSLR_FILE",
    help="Path to write output global SLR file.",
    required=True,
    type=str,
)
@click.option(
    "--output-lslr-file",
    envvar="TLM_STERODYNAMICS_OUTPUT_LSLR_FILE",
    help="Path to write output local SLR file.",
    required=True,
    type=str,
)
@click.option(
    "--climate-data-file",
    envvar="TLM_STERODYNAMICS_CLIMATE_DATA_FILE",
    help="NetCDF4/HDF5 file containing surface temperature data.",
    type=str,
    required=True,
)
@click.option(
    "--expansion-coefficients-file",
    envvar="TLM_STERODYNAMICS_EXPANSION_COEFFICIENTS_FILE",
    help="Path to NetCDF file containing expansion coefficients.",
    type=str,
    required=True,
)
@click.option(
    "--gsat-rmses-file",
    envvar="TLM_STERODYNAMICS_GSAT_RMSES_FILE",
    help="Path to NetCDF file containing GSAT RMSEs.",
    type=str,
    required=True,
)
@click.option(
    "--location-file",
    envvar="TLM_STERODYNAMICS_LOCATION_FILE",
    help="File containing name, id, lat, and lon of points for localization.",
    type=str,
    required=True,
)
@click.option(
    "--model-dir",
    envvar="TLM_STERODYNAMICS_MODEL_DIR",
    help="Directory containing ZOS/ZOSTOGA CMIP6 GCM output.",
    type=str,
    required=True,
)
@click.option(
    "--scenario",
    envvar="TLM_STERODYNAMICS_SCENARIO",
    help="SSP scenario (i.e ssp585) or temperature target (i.e. tlim2.0win0.25).",
    default="ssp585",
)
@click.option(
    "--scenario-dsl",
    envvar="TLM_STERODYNAMICS_SCENARIO_DSL",
    help="SSP scenario to use for correlation of thermal expansion and dynamic sea level, if not the same as scenario.",
    default="",
)
@click.option(
    "--no-drift-corr",
    envvar="TLM_STERODYNAMICS_NO_DRIFT_CORR",
    help="Do not apply the drift correction.",
    default=False,
)
@click.option(
    "--no-correlation",
    envvar="TLM_STERODYNAMICS_NO_CORRELATION",
    help="Do not apply the correlation between ZOS and ZOSTOGA fields.",
    default=False,
)
@click.option(
    "--baseyear",
    envvar="TLM_STERODYNAMICS_BASEYEAR",
    help="Base year to which projections are centered.",
    default=2000,
)
@click.option(
    "--pyear-start",
    envvar="TLM_STERODYNAMICS_PYEAR_START",
    help="Year for which projections start.",
    default=2020,
)
@click.option(
    "--pyear-end",
    envvar="TLM_STERODYNAMICS_PYEAR_END",
    help="Year for which projections end.",
    default=2300,
)
@click.option(
    "--pyear-step",
    envvar="TLM_STERODYNAMICS_PYEAR_STEP",
    help="Step size in years between start and end at which projections are produced.",
    default=10,
    type=click.IntRange(min=1),
)
@click.option(
    "--nsamps",
    envvar="TLM_STERODYNAMICS_NSAMPS",
    help="Number of samples to generate.",
    default=20000,
)
@click.option(
    "--seed",
    envvar="TLM_STERODYNAMICS_SEED",
    help="Seed value for random number generator.",
    default=1234,
)
@click.option(
    "--chunksize",
    envvar="TLM_STERODYNAMICS_CHUNKSIZE",
    help="Number of locations to process at a time [default=50].",
    default=50,
)
@click.option("--debug/--no-debug", default=False, envvar="TLM_STERODYNAMICS_DEBUG")
def main(
    pipeline_id,
    climate_data_file,
    expansion_coefficients_file,
    gsat_rmses_file,
    location_file,
    model_dir,
    scenario,
    scenario_dsl,
    no_drift_corr,
    no_correlation,
    baseyear,
    pyear_start,
    pyear_end,
    pyear_step,
    nsamps,
    seed,
    chunksize,
    output_gslr_file,
    output_lslr_file,
    debug,
) -> None:
    """
    Application producing thermal expansion and dynamic sea level projections. Thermal expansion is derived from inputted surface air temperature and ocean heat content projections provided from a climate model emulator. Dynamic sea level is estimated based on the correlation between thermal expansion and local dynamic sea level in the CMIP6 multimodel ensemble. See IPCC AR6 WG1 9.SM.4.2 and 9.SM.4.3.
    """
    if debug:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

    logger.info("Starting tlm-sterodynamics")

    logger.info("Starting thermal expansion preprocessing")
    te_pre_data = tlm_preprocess_thermalexpansion(
        scenario,
        pipeline_id,
        climate_data_file,
        expansion_coefficients_file,
        gsat_rmses_file,
    )
    logger.info("Thermal expansion preprocessing complete")

    if scenario_dsl == "":
        scenario_dsl = scenario

    logger.info("Starting ocean dynamics preprocessing")
    od_config, od_zostoga, od_zos = tlm_preprocess_oceandynamics(
        scenario_dsl,
        model_dir,
        no_drift_corr,
        no_correlation,
        pyear_start,
        pyear_end,
        pyear_step,
        location_file,
        baseyear,
        pipeline_id,
    )
    logger.info("Ocean dynamics preprocessing complete")

    logger.info("Starting thermal expansion fitting")
    te_fit_data = tlm_fit_thermalexpansion(te_pre_data)
    logger.info("Thermal expansion fitting complete")

    logger.info("Starting ocean dynamics fitting")
    _, od_oceandynamics_fit = tlm_fit_oceandynamics(
        od_config, od_zostoga, od_zos, pipeline_id
    )
    logger.info("Ocean dynamics fitting complete")

    logger.info("Starting thermal expansion projection")
    te_projections = tlm_project_thermalexpansion(
        te_pre_data,
        te_fit_data,
        seed,
        nsamps,
        pipeline_id,
        scenario,
        pyear_start,
        pyear_end,
        pyear_step,
        baseyear,
        output_gslr_file,
    )
    logger.info("Thermal expansion projection complete")

    logger.info("Starting ocean dynamics postprocessing")
    tlm_postprocess_oceandynamics(
        od_config,
        od_zos,
        od_oceandynamics_fit,
        te_projections,
        nsamps,
        seed,
        chunksize,
        output_lslr_file,
    )
    logger.info("Ocean dynamics postprocessing complete")

    logger.info("tlm-sterodynamics complete")
