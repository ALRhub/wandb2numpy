import argparse

from wandb2numpy.config_loader import load_config
from wandb2numpy.export import export_data
from wandb2numpy.save_experiment import create_output_dirs, save_matrix

parser = argparse.ArgumentParser(description='Export data from wandb to numpy array or csv')
parser.add_argument("config_path")
parser.add_argument('-o', action='store_true')
parser.add_argument('-e', '--experiments', nargs='+', default=None,
                       help='Allows to specify which experiments should be exported.')
args = parser.parse_args()



if __name__ == "__main__":
    config = load_config(args.config_path)

    experiment_data_dict, config_list = export_data(config, args.experiments)
    
    for i, experiment in enumerate(experiment_data_dict.keys()):
        experiment_dir = create_output_dirs(config_list[i], experiment)

        for field in experiment_data_dict[experiment]:
            save_matrix(experiment_data_dict[experiment], experiment_dir, field, args.o, config_list[i])