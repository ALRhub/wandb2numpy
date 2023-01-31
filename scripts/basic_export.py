import wandb2numpy

config = {}
config["my_exp"] = {}
config["my_exp"]["entity"] = "kit-alr"
config["my_exp"]["project"] = "wandb_export"
config["my_exp"]["fields"] = ["train_acc", "test_acc"]

data_dict, config_list = wandb2numpy.export_data(config)