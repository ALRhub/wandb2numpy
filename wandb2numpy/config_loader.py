import yaml

from copy import deepcopy
from typing import List, Tuple
from wandb2numpy import util

def load_config(config_path: str, experiment_list: List[str]) -> Tuple[dict, List[dict], List[str]]:
    """Loads a list of experiment configs and the default config from a config.yaml file. 
    If experiment list is not None, only the experiments in experiment_list are included.
    Arguments:
        config_path {str} -- path to the config.yaml file
        experiment_list {List[str]} -- a list of experiments to be exported. If None, all experiments are exported
    Returns:
        Tuple[dict, List[dict], List[str]] -- the default config, a list of all experiment configs, a list of all experiment names
    """
    with open(config_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            default_config = config.pop('DEFAULT', None)
            if default_config is None:
                print("No DEFAULT entry found in config")

            experiment_configs = []
            experiment_names = []
            for experiment in config.keys():
                if experiment in experiment_list or experiment_list is None:
                    experiment_configs.append(config[experiment])
                    experiment_names.append(experiment)

            return default_config, experiment_configs, experiment_names

        except yaml.YAMLError as exc:
            print(exc)

def merge_default(default_config: dict, experiment_configs: List[dict]) -> List[dict]:
    """merges each individual experiment configuration with the default parameters
    Arguments:
        default_config {dict} -- default configuration parameters
        experiment_configs {List[dict]} -- a list of individual experiment configurations
    Returns:
        List[dict] -- a list of all experiment configurations
    """
    if default_config is None:
        return experiment_configs

    expanded_exp_configs = []
    for c in experiment_configs:
        merge_c = deepcopy(default_config)
        merge_c = util.deep_update(merge_c, c)
        expanded_exp_configs.append(merge_c)

    return expanded_exp_configs