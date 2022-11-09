def get_filtered_runs(config, api):
    filter_list = []
    filter_dict = {}
    if "groups" in config.keys() and config["groups"] != "all":
        if not isinstance(config["groups"], list):
            print("Error: groups must be either 'all' or a list of group names")
        for i, group in enumerate(config["groups"]):
            filter_group_dict = build_filter_dict(i, group, config)
            filter_list.append(filter_group_dict)

        filter_dict["$or"] = filter_list

    if "config" in config.keys():
        filter_dict = append_filter_dict("config", config["config"], filter_dict)

    if "summary" in config.keys():
        filter_dict = append_filter_dict("summary_metrics", config["summary"], filter_dict)

    run_list = list(api.runs(config["entity"] + "/" + config["project"], filters=filter_dict))
    
    return run_list

def build_filter_dict(idx: int, group: str, config: dict) -> dict:
    filter_dict = {}
    filter_dict["group"] = group
    if 'job_types' in config.keys() and config['job_types'] != "all" and config['job_types'][idx] != "all":
        filter_dict["jobType"] = {}
        filter_dict["jobType"]["$in"] = config['job_types'][idx]

    if 'runs' in config.keys() and config['runs'] != "all" and config['runs'][idx] != "all":
        filter_dict["display_name"] = {}
        filter_dict["display_name"]["$in"] = config['runs'][idx]

    return filter_dict

def append_filter_dict(dict_name: str, param_dict: dict, filter_dict: dict) -> dict:
    for key in param_dict:
        filter_dict[f"{dict_name}.{key}"] = {}
        if "min" in param_dict[key].keys():
            filter_dict[f"{dict_name}.{key}"]["$gte"] = param_dict[key]["min"]
        if "max" in param_dict[key].keys():
            filter_dict[f"{dict_name}.{key}"]["$lte"] = param_dict[key]["max"]
        if "values" in param_dict[key].keys():
            filter_dict[f"{dict_name}.{key}"]["$in"] = param_dict[key]["values"]

    return filter_dict