# wandb2numpy

Export data from wandb as NumPy arrays or csv. Data to be exported can be specified in a YAML config file.

## Installation

### Automatic
The easiest way to install wandb2numpy is to run
```bash
pip install wandb2numpy
```
Afterwards, test your installation by calling `import wandb2numpy` from a Python environment.

### Manual
If you want to look at the code and potentially modify it, you can also manually install the package. To do that, clone this repository, enter the repository's directory and run

```bash
pip install .
```

## Usage

There are two ways that you can export your data: Via the command line or from within a Python script.
To export your data using the command line, the easiest way is to run:
```bash
wandb2numpy <your_config>.yaml
```

To overwrite previously exported data, use the `-o` flag. To run not all but only some experiments from the config file, add `-e my_experiment1 my_experiment2`.

In case you installed the package manually, you can also execute the Python script directly:
```bash
python ./export_data.py <your_config>.yaml
```

The other option is to use wandb2numpy from within a Python script. In order to do that, call the function like this:
```bash
import wandb2numpy
data_dict, config_list = wandb2numpy.export_data(config)
```
`config` needs to be a dictionary that corresponds to the structure of valid YAML files described below. You can provide a list for the optional parameter `experiment_list = my_list` to specify what experiments to run. The function will not save any data, it will only return the exported data in form of a dictionary as well as a list of configurations for all experiments that were used for the export. The returned dictionary has one entry for each experiment on the top level. On the level below, it contains a pandas dataframe or a numpy array for each field of the experiment, depending on the `output_data_type` in the config.

To understand the required structure of a config file as well as the possibilities for filtering, I recommend looking at the examplary config files in the folder `example_configs`.

All parameters in the config can either be defined in DEFAULT or in a specific experiment. If they are defined in both, the definition in the experiment overwrites the one in DEFAULT. There are some parameters that must be specified either in DEFAULT or in the experiments, and some that are optional. The name of the exported data frame is given by the experiment name in the config file (top level key). Your config can contain multiple experiments, the only restriction is that it needs to contain one at minimum.

Parameters that must be specified either in DEFAULT or in an experiment include:
* `entity`: entity that the WandB project belongs to.
* `project`: name of the WandB project.
* `fields`: List of metrics that should be exported.
* `output_path`: path to a directory where all output data will be stored. A subdirectory for each experiment will be created.

Additionally, there are a variety of optional parameters that can be used to filter the runs. If they are not specified, by default all runs are taken. Those optional parameters include:
* `groups`: run groups to be exported (list of group names). 
* `job_types`: job types to be exported (list of type names). If a list of groups is provided, the `job_types` list is expected to be nested, containing a list of job types for each group (length of group list and top level length of `job_types` list must be equal).
* `runs`: runs to be exported (list of run names). Same format as for `job_types` (see explanation above).
* `tags`:  tags to be exported (list of tag names). Same format as for `job_types` (see explanation above).
* `output_data_type`: can be either `"numpy"` or `"csv"` (default is to use NumPy)
* `history_samples`: Either `"all"` or number of steps from the history that are sampled (Integer). If not specified, 12k samples will be used. Due to a bug in the wandb API, this is the maximum supported sample size for now. A discussion on this can be found [**here**](https://community.wandb.ai/t/calling-run-history-samples-n-samples-returns-a-sample-size-different-from-n-samples/3414). Using full history will be very slow for runs with > 100k steps.
* `config`: dictionary of config entries.
* `summary`: dictionary of summary entries.

Each WandB run has both a config dictionary and a summary dictionary associated with it. Using the `config` and `summary` dictionaries mentioned above, runs can be filtered with regards to those attributes. Each entry in the dictionaries must specify either a list of allowed values (`values: ["value1", "value2"]`) or for numeric attributes a range in which they must lie. This is done by providing a `min` and/or a `max` value.

All of this is showcased in examplary config files in the folder `example_configs`.