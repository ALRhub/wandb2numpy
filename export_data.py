import argparse
import wandb
import sys

from tqdm import tqdm

from wandb2numpy import util
from wandb2numpy.config_loader import load_config, check_valid_configs, merge_default
from wandb2numpy.filtering import get_filtered_runs
from wandb2numpy.save_experiment import create_output_dirs, save_matrix

parser = argparse.ArgumentParser(description='Export data from wandb to numpy array or csv')
parser.add_argument("config_path")
parser.add_argument('-o', action='store_true')
parser.add_argument('-e', '--experiments', nargs='+', default=None,
                       help='Allows to specify which experiments should be exported.')
args = parser.parse_args()


if __name__ == "__main__":
    default_config, experiment_configs, experiment_names = load_config(args.config_path, args.experiments)
    valid_configs = check_valid_configs(default_config, experiment_configs, experiment_names)
    if not valid_configs:
        sys.exit("Aborting execution because of invalid config file")
    config_list = merge_default(default_config, experiment_configs)
    
    api = wandb.Api(timeout=15)

    for i, config in enumerate(config_list): 
        print(f"Processing experiment {experiment_names[i]} ...")
        run_list = get_filtered_runs(config, api)

        if not run_list:
            print("Warning: No matching runs founds for this experiment. Skipping...")
            continue

        print("Found following runs that match the filters:")
        for run in run_list:
            print(run.name)

        if 'history_samples' in config.keys():
            print(f"Using sampled history of runs with sample size {config['history_samples']}. Runs that are shorter than that keep their original length.")

        all_runs_dict = {}

        for j, run in enumerate(tqdm(run_list)):
            current_run_dict = util.extract_data(run, config["fields"], config)
            all_runs_dict[j] = current_run_dict

        np_all_runs_dict = util.outer_dict_to_np_array(all_runs_dict)
        experiment_dir = create_output_dirs(config, experiment_names[i])

        for field in np_all_runs_dict.keys():
            save_matrix(np_all_runs_dict, experiment_dir, field, args.o, config)