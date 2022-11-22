import yaml

from copy import deepcopy
from typing import List, Tuple
from wandb2numpy import util


def load_config(config_path: str) -> dict:
    with open(config_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            return config

        except yaml.YAMLError as exc:
            print(exc)

def parse_config(config: dict, experiment_list: List[str]) -> Tuple[dict, List[dict], List[str]]:
    """Extracts a list of experiment configs and the default config from a config dictionary. 
    If experiment list is not None, only the experiments in experiment_list are included.
    Arguments:
        config {dict} -- config dictionary
        experiment_list {List[str]} -- a list of experiments to be exported. If None, all experiments are exported
    Returns:
        Tuple[dict, List[dict], List[str]] -- the default config, a list of all experiment configs, a list of all experiment names
    """
    default_config = config.pop('DEFAULT', None)
    if default_config is None:
        print("No DEFAULT entry found in config")

    experiment_configs = []
    experiment_names = []
    for experiment in config.keys():
        if experiment_list is None or experiment in experiment_list:
            experiment_configs.append(config[experiment])
            experiment_names.append(experiment)

    return default_config, experiment_configs, experiment_names

def check_valid_configs(default_config, experiment_configs, experiment_names):
    # entity, project, fields and output_path must be specified either in default or in each experiment
    required_params = ["entity", "project", "fields", "output_path"]
    optional_filter_lists = ["groups", "job_types", "runs"]
    optional_filter_dicts = ["config, summary"]

    for parameter in required_params:
        if default_config is None or parameter not in default_config.keys():
            for i, exp_config in enumerate(experiment_configs):
                if parameter not in exp_config.keys():
                    print(f"Error: {parameter} is neither specified in DEFAULT nor in {experiment_names[i]}")
                    return False

    # check that all parameters have the correct format if they are included
    if default_config is not None:
        is_valid_config = check_data_types(default_config, "DEFAULT", required_params, optional_filter_lists, optional_filter_dicts)
        
        if not is_valid_config:
                return False

    for j, exp_config in enumerate(experiment_configs):
        is_valid_config = check_data_types(exp_config, experiment_names[j], required_params, optional_filter_lists, optional_filter_dicts)
        if not is_valid_config:
            return False

    return True

def check_data_types(config: dict, config_name: str, required_params: List, optional_filter_lists: List, optional_filter_dicts: List):
    for required_param in required_params:
            if required_param in config.keys():
                if not isinstance(required_param, str):
                    print(f"Error: {required_param} in {config_name} is not of type String")
                    return False

    for opt_list in optional_filter_lists:
        if opt_list in config.keys():
            if not isinstance(config[opt_list], List) and config[opt_list] != "all":
                print(f"Error: {opt_list} in {config_name} is not of type List or equal to 'all'")
                return False

    for opt_dict in optional_filter_dicts:
        if opt_dict in config.keys():
            if not isinstance(config[opt_dict], dict):
                print(f"Error: {opt_dict} in {config_name} is not of type Dict")
                return False

    # if groups are provided as a list, runs and job_types must be nested lists with equal length (if they are provided)
    if 'groups' in config.keys() and config['groups'] != "all":
        if not check_nested_list('job_types', config):
            return False
        if not check_nested_list('runs', config):
            return False
        if not check_nested_list('tags', config):
            return False
    else:
        if not check_not_nested('job_types', config):
            return False
        if not check_not_nested('runs', config):
            return False
        if not check_not_nested('tags', config):
            return False

    return True

def check_nested_list(param_name: str, config: dict):
    if param_name in config.keys():
        if config[param_name] != "all" and len(config[param_name]) != len(config['groups']):
            print(f"Error: List of {param_name} must have the same length as groups list")
            return False
        elif config[param_name] != "all":
            for entry in config[param_name]:
                if not isinstance(entry, List) and entry != "all":
                    print(f"Error: {param_name} must be a nested list if groups are provided as a list")
                    return False
    return True

def check_not_nested(param_name: str, config: dict):
    if param_name in config.keys() and config[param_name] != "all":
        for entry in config[param_name]:
            if not isinstance(entry, str):
                print(f"Error: {param_name} must be a flat list of Strings if groups list is not provided")
                return False
    return True

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