import wandb2numpy


config = {}
config["my_exp"] = {}
config["my_exp"]["entity"] = "kit-alr"
config["my_exp"]["project"] = "wandb_export"
config["my_exp"]["groups"] = ["fmnist_dropout_cnn_new_gmore_elbo_mean_kl_standard_hpo_algo_1_env_1"]
config["my_exp"]["fields"] = ["train_acc", "test_acc"]

data_dict, config_list = wandb2numpy.export_data(config, by_group_and_job_type=True)
print(data_dict)
