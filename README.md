# wandb2numpy

Export data from wandb as NumPy arrays or csv. Data to be exported can be specified in a YAML config file.

## Usage

To export your data, enter the repository's directory and run

```bash
pip install .
python ./export_data.py <your_config>.yaml

```
To overwrite previously exported data, use the `-o` flag. To run not all but only some experiments from the config file, add `-e my_experiment1 my_experiment2`.

All parameters in the config file can either be defined in DEFAULT or in a specific experiment. If they are defined in both, the definition in the experiment overwrites the one in DEFAULT. There are some parameters that must be specified either in DEFAULT or in the experiments, and some that are optional. The name of the exported data frame is given by the experiment name in the config file (top level key). Your config can contain multiple experiments, the only restriction is that it needs to contain one at minimum.

Parameters that must be specified either in DEFAULT or in an experiment include:
* `entity`: entity that the WandB project belongs to.
* `project`: name of the WandB project.
* `fields`: List of metrics that should be exported.
* `output_path`: path to a directory where all output data will be stored. A subdirectory for each experiment will be created.

Additionally, there are a variety of optional parameters that can be used to filter the runs. If they are not specified, by default all runs are taken. Those optional parameters include:
* `groups`: run groups to be exported (list of group names).
* `job_types`: job types to be exported (list of type names).
* `runs`: runs to be exported (list of run names).
* `output_data_type`: can be either `"numpy"` or `"csv"` (default is to use NumPy)
* `history_samples`: Either `"all"` or number of steps from the history that are sampled (Integer). If not specified, 12k samples will be used. Due to a bug in the wandb API, this is the maximum supported sample size for now. A discussion on this can be found [**here**](https://community.wandb.ai/t/calling-run-history-samples-n-samples-returns-a-sample-size-different-from-n-samples/3414). Using full history will be very slow for runs with > 100k steps.
* `config`: dictionary of config entries.
* `summary`: dictionary of summary entries.

Each WandB run has both a config dictionary and a summary dictionary associated with it. Using the `config` and `summary` dictionaries mentioned above, runs can be filtered with regards to those attributes. Each entry in the dictionaries must specify either a list of allowed values (`values: ["value1", "value2"]`) or for numeric attributes a range in which they must lie. This is done by providing a `min` and/or a `max` value.

All of this is showcased in examplary config files in the folder `example_configs`.