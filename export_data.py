import argparse
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

# group_dict 
def outer_dict_to_np_array(group_dict):
    n_runs = len(group_dict)
    output_dict = {}
    for field in group_dict[0]:
        max_steps = max([len(group_dict[i][field]) for i in range(n_runs)])
        output_array = np.zeros((n_runs, max_steps))
        for run in group_dict:
            steps = group_dict[run][field].shape[0]
            if steps == max_steps: # check if array has length max_steps, otherwise pad to that size with zeros (in the end)
                output_array[run] = group_dict[run][field]
            else:
                output_array[run] = np.pad(group_dict[run][field], (0, max_steps - steps))
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

def save_matrix(matrix_dict, experiment_dir, field, overwrite_flag):
    file_path = os.path.join(experiment_dir, field)
    if os.path.isfile(file_path + ".npy") and not overwrite_flag:
        print("File " + file_path + ".npy already exists! To overwrite, rerun script with --o flag.")
    else:
        with open(file_path + ".npy", 'wb') as f:
            np.save(f, matrix_dict[field])
        print("Saved File " + file_path + ".npy, shape of NP array is " + str(matrix_dict[field].shape))

def filter_match(filter_param, run_param):
    if filter_param == "all":
        return True
    else:
        return run_param in filter_param

def get_filtered_runs(config, experiment):
    run_list = []
    for i, group in enumerate(config[experiment]['groups']):
        filter_dict = {"group": group}
        runs = list(api.runs(config["default"]["entity"] + "/" + config["default"]["project"], filters=filter_dict))

        if config[experiment]['job_types'][i] == "all" and config[experiment]['runs'][i] == "all":
            run_list.extend(runs)
        else:
            for run in runs:
                if filter_match(config[experiment]['job_types'][i], run.job_type) and filter_match(config[experiment]['runs'][i], run.name):
                    run_list.append(run)
            
    return run_list

if __name__ == "__main__":
    config = load_config(args.config_path)
    
    experiments = list(config.keys())
    experiments.remove("default")

    api = wandb.Api()

    for experiment in experiments: 
        runs = get_filtered_runs(config, experiment)
        print("Found following runs that match the filters:")
        for run in runs:
            print(run.name)

        group_dict = {}
        try:
            for i, run in enumerate(tqdm(runs)):
                run_dict = extract_data(run, config["default"]["fields"])
                group_dict[i] = run_dict

            np_group_dict = outer_dict_to_np_array(group_dict)

            experiment_dir = create_output_dirs(config, experiment)

            for field in np_group_dict.keys():
                save_matrix(np_group_dict, experiment_dir, field, args.o)
                
        except requests.exceptions.HTTPError:
            print(f"Error loading {config[experiment]['group']}.")