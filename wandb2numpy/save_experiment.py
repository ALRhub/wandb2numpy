import numpy as np
import os
import pandas as pd

def create_output_dirs(config: str, experiment: str) -> str:
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

def save_matrix(matrix_dict, experiment_dir, field, overwrite_flag, config):
    # If field name contains "/", create subdirectory to reflect hierarchic field structure
    if "/" in field:
        str_parts = field.split("/")
        for idx in range(len(str_parts) - 1):
            experiment_dir = os.path.join(experiment_dir, str_parts[idx])
            isdir_experiment = os.path.isdir(experiment_dir)
            if not isdir_experiment:
                os.mkdir(experiment_dir)
        file_path = os.path.join(experiment_dir, str_parts[-1])
            
    else:
        file_path = os.path.join(experiment_dir, field)

    if "output_data_type" in config.keys() and config["output_data_type"] == "csv": # CSV
        if os.path.isfile(file_path + ".csv") and not overwrite_flag:
            print("Error: File " + file_path + ".csv already exists! To overwrite, rerun script with -o flag.")
        else:
            with open(file_path + ".csv", 'wb') as f:
                matrix_dict[field].to_csv(f)
                print("Saved Pandas DataFrame to file " + file_path + ".csv, shape of array is " + str(matrix_dict[field].shape))
    
    elif not "output_data_type" in config.keys() or config["output_data_type"] == "numpy": # NumPy 
        if os.path.isfile(file_path + ".npy") and not overwrite_flag:
            print("Error: File " + file_path + ".npy already exists! To overwrite, rerun script with -o flag.")
        else:
            with open(file_path + ".npy", 'wb') as f:
                np.save(f, matrix_dict[field])
            print("Saved NumPy array to file " + file_path + ".npy, shape of array is " + str(matrix_dict[field].shape))
    
    else:
        print(f"Error: {config['output_data_type']} is not a valid output format. Possible formats are 'numpy' and 'csv'")