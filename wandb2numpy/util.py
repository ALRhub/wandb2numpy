import numpy as np

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

def extract_data(run, fields):
    history = run.scan_history()

    data_dict = {}
    for key in fields:
        data_list = []
        for data_point in history:
            if not key in data_point.keys():
                print(f"Error: Run {run.name} does not have a field called {key}")
                break
            data_list.append(data_point[key])
        data_dict[key] = np.array(data_list)
        #data_dict[key] = np.array([data_point[key] for data_point in history])
    return data_dict

def outer_dict_to_np_array(group_dict):
    n_runs = len(group_dict)
    output_dict = {}
    for field in group_dict[0]:
        max_steps = max([len(group_dict[i][field]) for i in range(n_runs)])
        output_array = np.zeros((n_runs, max_steps))
        for run in group_dict:
            steps = group_dict[run][field].shape[0]
            if steps == max_steps: # check if array has length max_steps, otherwise pad to that size with NaNs (in the end)
                output_array[run] = group_dict[run][field]
            else:
                output_array[run] = pad_run(group_dict[run][field], max_steps)
                
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