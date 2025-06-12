"""
Logic for the CLI.
"""

import click

from tlm_sterodynamics.tlm_sterodynamics_preprocess_thermalexpansion import (
    tlm_preprocess_thermalexpansion,
)
from tlm_sterodynamics.tlm_sterodynamics_fit_thermalexpansion import (
    tlm_fit_thermalexpansion,
)
from tlm_sterodynamics.tlm_sterodynamics_project import tlm_project_thermalexpansion


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
    "--scenario",
    envvar="TLM_STERODYNAMICS_SCENARIO",
    help="SSP scenario (i.e ssp585) or temperature target (i.e. tlim2.0win0.25).",
    default="rcp85",
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
def main(
    pipeline_id,
    climate_data_file,
    expansion_coefficients_file,
    gsat_rmses_file,
    scenario,
    baseyear,
    pyear_start,
    pyear_end,
    pyear_step,
    nsamps,
    seed,
    output_gslr_file,
) -> None:
    """
    Application producing thermal expansion and dynamic sea level projections. Thermal expansion is derived from inputted surface air temperature and ocean heat content projections provided from a climate model emulator. Dynamic sea level is estimated based on the correlation between thermal expansion and local dynamic sea level in the CMIP6 multimodel ensemble. See IPCC AR6 WG1 9.SM.4.2 and 9.SM.4.3.
    """
    click.echo("Hello from tlm-sterodynamics!")

    processed_data = tlm_preprocess_thermalexpansion(
        scenario,
        pipeline_id,
        climate_data_file,
        expansion_coefficients_file,
        gsat_rmses_file,
    )
    fit_data = tlm_fit_thermalexpansion(processed_data)
    _ = tlm_project_thermalexpansion(
        processed_data,
        fit_data,
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
