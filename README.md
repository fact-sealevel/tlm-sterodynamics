# tlm-sterodynamics

Application producing thermal expansion and dynamic sea level projections. Thermal expansion is derived from inputted surface air temperature and ocean heat content projections provided from a climate model emulator. Dynamic sea level is estimated based on the correlation between thermal expansion and local dynamic sea level in the CMIP6 multimodel ensemble. See IPCC AR6 WG1 9.SM.4.2 and 9.SM.4.3.

> [!CAUTION]
> This is a prototype. It is likely to change in breaking ways. It might delete all your data. Don't use it in production.

## Example

This application can run on data projected climate data. For example, you can use the output `climate.nc` file from the [the fair model container](https://github.com/fact-sealevel/fair-temperature). Additional input data is also needed.

First, create a new directory and download required input data and prepare for the run, like

```shell
# Input data we will pass to the container
mkdir -p ./data/input
curl -sL https://zenodo.org/record/7478192/files/tlm_sterodynamics_preprocess_data.tgz | tar -zx -C ./data/input
curl -sL https://zenodo.org/record/7478192/files/tlm_sterodynamics_cmip6_data.tgz | tar -zx -C ./data/input

echo "New_York	12	40.70	-74.01" > ./data/input/location.lst

# Output projections will appear here
mkdir -p ./data/output
```

With fair output as an example, drop the `climate.nc` file into `./data/input`.

Now run the container, for example with Docker, like

```shell
docker run --rm \
  -v ./data/input:/input/:ro \
  -v ./data/output:/output \
  ghcr.io/fact-sealevel/tlm-sterodynamics:latest \
  --pipeline-id=1234 \
  --scenario="ssp585" \
  --nsamps=10 \
  --output-gslr-file="/output/gslr.nc" \
  --output-lslr-file="/output/lslr.nc" \
  --climate-data-file="/input/climate.nc" \
  --location-file="/input/location.lst" \
  --model-dir="/input/cmip6/" \
  --expansion-coefficients-file="/input/scmpy2LM_RCMIP_CMIP6calpm_n18_expcoefs.nc" \
  --gsat-rmses-file="/input/scmpy2LM_RCMIP_CMIP6calpm_n17_gsat_rmse.nc"
```

If the run is successful, the output projection will appear in `./data/output`.

> [!TIP]
> For this example we use `ghcr.io/fact-sealevel/tlm-sterodynamics:latest`. We do not recommend using `latest` for production runs because it will grab the latest release. This means runs will not be reproducible and may include breaking changes. Instead, use a tag for a specific version of the image or an image's digest hash. You can find tagged image versions and digests [here](https://github.com/fact-sealevel/tlm-sterodynamics/pkgs/container/tlm-sterodynamics).

## Features

Several options and configurations are available when running the container.

```
Usage: tlm-sterodynamics [OPTIONS]

  Application producing thermal expansion and dynamic sea level projections.
  Thermal expansion is derived from inputted surface air temperature and ocean
  heat content projections provided from a climate model emulator. Dynamic sea
  level is estimated based on the correlation between thermal expansion and
  local dynamic sea level in the CMIP6 multimodel ensemble. See IPCC AR6 WG1
  9.SM.4.2 and 9.SM.4.3.

Options:
  --pipeline-id TEXT              Unique identifier for this instance of the
                                  module.  [required]
  --output-gslr-file TEXT         Path to write output global SLR file.
                                  [required]
  --output-lslr-file TEXT         Path to write output local SLR file.
                                  [required]
  --climate-data-file TEXT        NetCDF4/HDF5 file containing surface
                                  temperature data.  [required]
  --expansion-coefficients-file TEXT
                                  Path to NetCDF file containing expansion
                                  coefficients.  [required]
  --gsat-rmses-file TEXT          Path to NetCDF file containing GSAT RMSEs.
                                  [required]
  --location-file TEXT            File containing name, id, lat, and lon of
                                  points for localization.  [required]
  --model-dir TEXT                Directory containing ZOS/ZOSTOGA CMIP6 GCM
                                  output.  [required]
  --scenario TEXT                 SSP scenario (i.e ssp585) or temperature
                                  target (i.e. tlim2.0win0.25).
  --scenario-dsl TEXT             SSP scenario to use for correlation of
                                  thermal expansion and dynamic sea level, if
                                  not the same as scenario.
  --no-drift-corr BOOLEAN         Do not apply the drift correction.
  --no-correlation BOOLEAN        Do not apply the correlation between ZOS and
                                  ZOSTOGA fields.
  --baseyear INTEGER              Base year to which projections are centered.
  --pyear-start INTEGER           Year for which projections start.
  --pyear-end INTEGER             Year for which projections end.
  --pyear-step INTEGER RANGE      Step size in years between start and end at
                                  which projections are produced.  [x>=1]
  --nsamps INTEGER                Number of samples to generate.
  --seed INTEGER                  Seed value for random number generator.
  --chunksize INTEGER             Number of locations to process at a time
                                  [default=50].
  --help                          Show this message and exit.
 ```

See this help documentation by running:

```shell
docker run --rm ghcr.io/fact-sealevel/tlm-sterodynamics:latest --help
```

These options and configurations can also be set with environment variables prefixed by TLM_STERODYNAMICS_*. For example, set --gsat-rmses-file as an environment variable with TLM_STERODYNAMICS_GSAT_RMSES_FILE.

The program will take advantage of all available CPU cores to run faster, project local ocean dynamics in parallel across batches of locations. You can control the size of these baches with `--chunksize`. Using larger batches will generally speed up calculation but also increase memory use. The default setting is sensible if you are projecting samples on the magnitude of 10,000s samples or less. When run as a container, you can throttle the program's access to CPU cores. With `docker run` this done with the `--cpus` flag.

## Building the container locally

You can build the container with Docker by cloning the repository locally and then running

```shell
docker build -t tlm-sterodynamics:dev .
```

from the repository root.

## Support

Source code is available online at https://github.com/fact-sealevel/tlm-sterodynamics. This software is open source, available under the MIT license.

Please file issues in the issue tracker at https://github.com/fact-sealevel/tlm-sterodynamics/issues.
