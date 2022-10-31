import argparse
from genericpath import isfile
import os
import numpy as np
import requests
import wandb
import yaml

from tqdm import tqdm

parser = argparse.ArgumentParser(description='Export data from wandb to numpy array or pandas dataframe')
parser.add_argument("config_path")
parser.add_argument('--o', action='store_true')
args = parser.parse_args()

def extract_data(run, fields):
    history = run.scan_history()
    data_dict = {}
    for key in fields:
        data_dict[key] = np.array([data_point[key] for data_point in history])
    return data_dict

def outer_dict_to_np_array(group_dict):
    rep_dim = len(group_dict)
    output_dict = {}
    for field in group_dict[0]:
        steps = len(group_dict[0][field])
        output_array = np.zeros((rep_dim, steps))
        for rep in group_dict:
            output_array[rep] = group_dict[rep][field]
        output_dict[field] = output_array
    return output_dict

def load_config(config_path):
    with open(config_path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            print(exc)

def create_output_dirs(config, experiment):
    output_path = config["default"]["output_path"]

    data_dir = os.path.join(".", output_path)
    isdir_data = os.path.isdir(data_dir)
    if not isdir_data:
        os.mkdir(data_dir)

    experiment_dir = os.path.join(data_dir, experiment)
    isdir_experiment = os.path.isdir(experiment_dir)
    if not isdir_experiment:
        os.mkdir(experiment_dir)
    return experiment_dir

def save_matrix(experiment_dir, field, overwrite_flag):
    file_path = os.path.join(experiment_dir, field)
    if os.path.isfile(file_path + ".npy") and not overwrite_flag:
        print("File " + file_path + ".npy already exists! To overwrite, rerun script with --o flag.")
    else:
        with open(file_path + ".npy", 'wb') as f:
            np.save(f, np_group_dict[field])
        print("Saved file " + file_path + ".npy")

if __name__ == "__main__":
    config = load_config(args.config_path)
    
    experiments = list(config.keys())
    experiments.remove("default")

    api = wandb.Api()

    for experiment in experiments:
        filter_dict = {"group": config[experiment]["group"]}
        runs = api.runs(config["default"]["entity"] + "/" + config["default"]["project"], filters=filter_dict)
        group_dict = {}
        try:
            print(f"Started processing {config[experiment]['group']}...")
            for i, run in enumerate(tqdm(runs)):
                if config[experiment]["job_type"] != "all" and run.job_type != config[experiment]["job_type"]:
                    continue
                run_dict = extract_data(run, config["default"]["fields"])
                group_dict[i] = run_dict

            np_group_dict = outer_dict_to_np_array(group_dict)

            experiment_dir = create_output_dirs(config, experiment)

            for field in np_group_dict.keys():
                save_matrix(experiment_dir, field, args.o)
                
        except requests.exceptions.HTTPError:
            print(f"Error loading {config[experiment]['group']}.")