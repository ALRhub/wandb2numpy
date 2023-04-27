import wandb
import sys

from collections import defaultdict
from tqdm import tqdm
from typing import Dict, List, Tuple
from wandb2numpy import util

from wandb2numpy.config_loader import parse_config, check_valid_configs, merge_default
from wandb2numpy.filtering import get_filtered_runs


def export_data(config: Dict,
                experiments_list: List[str] = None,
                from_command_line: bool = False,
                by_group_and_job_type: bool = False,
                ) -> Tuple[Dict[str, any], List[Dict]]:
    """Exports data to numpy or pandas, according to specifications provided in the config dictionary
    Arguments:
        config {dict} -- config dictionary
        experiment_list {List[str]} -- a list of experiments to be exported. If None, all experiments are exported.
        from_command_line {bool} -- ?
        by_group_and_job_type {bool} -- If true, the runs are grouped by wandb group name and job type
    Returns:
        experiment_data_dict {dict} -- One top-level entry per exported experiment. On the next level, one entry per exported field.
        Value for each field is either a pandas dataframe or a numpy array, 
        depending on the specification in the config dict.
        config_list {List[dict]} -- List of individual configs for each experiment after inheriting from and overwriting DEFAULT
    """
    default_config, experiment_configs, experiment_names = parse_config(config, experiments_list)
    valid_configs = check_valid_configs(default_config, experiment_configs, experiment_names, from_command_line)
    if not valid_configs:
        sys.exit("Aborting execution because of invalid config file")
    config_list = merge_default(default_config, experiment_configs)
    
    api = wandb.Api(timeout=15)

    experiment_data_dict = {}

    for i, config in enumerate(config_list): 
        print(f"Processing experiment {experiment_names[i]} ...")
        run_list = get_filtered_runs(config, api)

        if not run_list:
            print("Warning: No matching runs founds for this experiment. Skipping...")
            continue

        print("Found following runs that match the filters:")
        for run in run_list:
            print(run.name)

        if 'history_samples' in config.keys() and config['history_samples'] != "all":
            print(f"Using sampled history of runs with sample size {config['history_samples']}. Runs that are shorter than that keep their original length.")

        all_runs_dict = util.nested_dict()

        for j, run in enumerate(tqdm(run_list)):
            current_run_dict = util.extract_data(run, config["fields"], config)
            if by_group_and_job_type:
                all_runs_dict[run.group][run.job_type].append(current_run_dict)
            else:
                all_runs_dict[j] = current_run_dict

        if by_group_and_job_type:
            out = util.nested_dict(dict)
            for group_name, group_runs in all_runs_dict.items():
                for job_type, runs in group_runs.items():
                    field_dict = util.run_dict_to_field_dict({k: v for k, v in enumerate(runs)}, config)
                    out[group_name][job_type] = field_dict
            experiment_data_dict[experiment_names[i]] = util.default_to_regular(out)
        else:
            field_dict = util.run_dict_to_field_dict(all_runs_dict, config)
            experiment_data_dict[experiment_names[i]] = field_dict

    return experiment_data_dict, config_list
