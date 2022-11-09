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
    file_path = os.path.join(experiment_dir, field)
    if os.path.isfile(file_path + ".npy") and not overwrite_flag:
        print("File " + file_path + ".npy already exists! To overwrite, rerun script with --o flag.")
    else:   
        if not "output_data_type" in config.keys() or config["output_data_type"] == "numpy":
            with open(file_path + ".npy", 'wb') as f:
                np.save(f, matrix_dict[field])
            print("Saved NumPy array to file " + file_path + ".npy, shape of array is " + str(matrix_dict[field].shape))
        elif config["output_data_type"] == "csv":
            row_names = [f"run {i}" for i in range(0, matrix_dict[field].shape[0])]
            column_names = [f"step {i}" for i in range(0, matrix_dict[field].shape[1])]
            df = pd.DataFrame(matrix_dict[field], index = row_names, columns = column_names)
            with open(file_path + ".csv", 'wb') as f:
                df.to_csv(f)
            print("Saved Pandas DataFrame to file " + file_path + ".csv, shape of array is " + str(matrix_dict[field].shape))
        else:
            print(f"Error: {config['output_data_type']} is not a valid output format. Possible formats are 'numpy' and 'csv'")
        