# wandb2numpy

Export data from wandb as numpy arrays or panda dataframes. Data to be exported can be specified in a YAML config file.

## Usage

To export your data, run

```bash

python .\export_data.py <your_config>.yaml

```
To overwrite previously exported data, use the `--o` flag.

Your config file needs to follow the format of `example_config.yaml`. It needs to contain the following parameters:
* name of exported data frame
* groups  to be exported (list of group names)
* job types to be exported (Either "all" or a nested list of type names, one list per group in the groups list)
* runs to be exported (Either "all" or a nested list of run names, one list per group in the groups list)
* data fields to be exported
* output data path
* entity that the wandb project belongs to
* name of the wandb project