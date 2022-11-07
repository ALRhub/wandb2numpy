import argparse
import os
import numpy as np
import requests
import wandb
import yaml

from copy import deepcopy
from tqdm import tqdm
from typing import List

from wandb2numpy import util

parser = argparse.ArgumentParser(description='Export data from wandb to numpy array or pandas dataframe')
parser.add_argument("config_path")
parser.add_argument('--o', action='store_true')
args = parser.parse_args()

def load_config(config_path):
    with open(config_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            default_config = config.pop('DEFAULT', None)
            if default_config is None:
                print("No DEFAULT entry found in config")

            experiment_configs = []
            experiment_names = []
            for experiment in config.keys():
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

def create_output_dirs(config, experiment):
    output_path = config["output_path"]

    data_dir = os.path.join(".", output_path)
    isdir_data = os.path.isdir(data_dir)
    if not isdir_data:
        os.mkdir(data_dir)

    experiment_dir = os.path.join(data_dir, experiment)
    isdir_experiment = os.path.isdir(experiment_dir)
    if not isdir_experiment:
        os.mkdir(experiment_dir)
    return experiment_dir

def save_matrix(matrix_dict, experiment_dir, field, overwrite_flag):
    file_path = os.path.join(experiment_dir, field)
    if os.path.isfile(file_path + ".npy") and not overwrite_flag:
        print("File " + file_path + ".npy already exists! To overwrite, rerun script with --o flag.")
    else:
        with open(file_path + ".npy", 'wb') as f:
            np.save(f, matrix_dict[field])
        print("Saved File " + file_path + ".npy, shape of NP array is " + str(matrix_dict[field].shape))


def get_filtered_runs(config):
    filter_dict = {}
    if "groups" in config.keys() and config["groups"] != "all":
        filter_dict = {"group": {"$in": config["groups"]}}
        
    run_list = list(api.runs(config["entity"] + "/" + config["project"], filters=filter_dict))
    run_list_filtered = []

    if 'job_types' in config.keys() and config['job_types'] == "all" and 'runs' in config.keys() and config['runs'] == "all":
        run_list_filtered = run_list
    else:
        for run in run_list:
            if util.filter_match(config, 'job_types', run.job_type) and util.filter_match(config, 'runs', run.name):
                run_list_filtered.append(run)
    
    return run_list_filtered

if __name__ == "__main__":
    default_config, experiment_configs, experiment_names = load_config(args.config_path)
    config_list = merge_default(default_config, experiment_configs)
    
    api = wandb.Api()

    for i, config in enumerate(config_list): 
        print(f"Processing experiment {experiment_names[i]} ...")
        runs = get_filtered_runs(config)
        print("Found following runs that match the filters:")
        for run in runs:
            print(run.name)

        group_dict = {}
        try:
            for j, run in enumerate(tqdm(runs)):
                run_dict = util.extract_data(run, config["fields"])
                group_dict[j] = run_dict

            np_group_dict = util.outer_dict_to_np_array(group_dict)

            experiment_dir = create_output_dirs(config, experiment_names[i])

            for field in np_group_dict.keys():
                save_matrix(np_group_dict, experiment_dir, field, args.o)
                
        except requests.exceptions.HTTPError:
            print(f"Error loading {config[experiment_names[i]]['group']}.")