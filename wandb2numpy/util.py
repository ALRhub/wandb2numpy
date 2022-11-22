import numpy as np
import pandas as pd
from tqdm import tqdm

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

def extract_data(run, fields, config):
    max_samples = 12000
    if 'history_samples' in config.keys():
        if config['history_samples'] == "all":
            history = run.scan_history()
        else:
            if not isinstance(config['history_samples'], int):
                tqdm.write(f"Error: history_samples must be 'all' or of type Integer")
                history = []
            else:
                n_samples = min(config['history_samples'], max_samples)
                history = run.history(keys=fields, samples=n_samples, pandas=False)
    else:
        history = run.history(keys=fields, samples=max_samples, pandas=False)
        

    data_dict = {}
    for key in fields:
        data_list = []
        is_valid_key = True
        for data_point in history:
            if not key in data_point.keys():
                tqdm.write(f"Warning: Run {run.name} does not have a field called {key}")
                is_valid_key = False
                break
            if is_valid_key:
                data_list.append(data_point[key])
        data_dict[key] = np.array(data_list)
    return data_dict

def run_dict_to_field_dict(run_dict, config):
    n_runs = len(run_dict)
    output_dict = {}
    for field in run_dict[0]:
        non_empty_runs = [run_dict[i][field] for i in range(n_runs) if len(run_dict[i][field]) != 0]
        n_non_empty_runs = len(non_empty_runs)
        if n_non_empty_runs > 0:
            max_steps = max([len(run) for run in non_empty_runs])
        else:
            max_steps = 0
        
        print(f"Number of runs that include field {field}: {n_non_empty_runs}")
        output_array = np.zeros((n_non_empty_runs, max_steps))
        for k, run in enumerate(non_empty_runs):
            steps = run.shape[0]
            if steps == max_steps: # check if array has length max_steps, otherwise pad to that size with NaNs (in the end)
                output_array[k] = run
            else:
                output_array[k] = pad_run(run, max_steps)
        if "output_data_type" in config.keys() and config["output_data_type"] == "csv":
            row_names = [f"run {i}" for i in range(0, output_array.shape[0])]
            column_names = [f"step {i}" for i in range(0, output_array.shape[1])]
            df = pd.DataFrame(output_array, index = row_names, columns = column_names)
            output_dict[field] = df
        else:
            output_dict[field] = output_array
    return output_dict

def pad_run(array, max_steps):
    steps = array.shape[0]
    print(f"Warning: Run has {max_steps - steps} steps less than longest run, padding array with NaNs")
    return np.pad(array, (0, max_steps - steps), 'constant', constant_values=np.nan)


def deep_update(base_dict: dict, update_dict: dict) -> dict:
    """Updates the base dictionary with corresponding values from the update dictionary, including nested collections.
       Not updated values are kept as is.
    Arguments:
        base_dict {dict} -- dictionary to be updated
        update_dict {dict} -- dictianry holding update values
    Returns:
        dict -- dictanry with updated values
    """
    for key, value in update_dict.items():
        # Update Recursively
        if isinstance(value, Mapping):
            branch = deep_update(base_dict.get(key, {}), value)
            base_dict[key] = branch
        else:
            base_dict[key] = update_dict[key]
    return base_dict

def filter_match(config, filter_param, run_param):
    if not filter_param in config.keys():
        return True
    elif config[filter_param] == "all":
        return True
    else:
        return run_param in config[filter_param]