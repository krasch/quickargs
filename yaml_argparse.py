import argparse

import yaml


def parse_arguments_based_on_yaml(yaml_file):
    with open(yaml_file) as f:
        yaml_data = yaml.load(f)

    yaml_flat = flatten_dict([], yaml_data)
    parser = argparse.ArgumentParser()
    for key, value in yaml_flat:
        key = ".".join(key)
        parser.add_argument("-{}".format(key), default=value)
    args = parser.parse_args()

    args_as_dict = vars(args)
    for key, value in args_as_dict.items():
        yaml_data[key] = value
    return yaml_data


def flatten_dict(current_key_hierarchy, sub_params):
    if isinstance(sub_params, dict):
        sub_result_nested = [flatten_dict(current_key_hierarchy + [key], val) for key, val in sub_params.items()]
        sub_result_flattened = [s for sub in sub_result_nested for s in sub]
        return sub_result_flattened
    else:
        return [(current_key_hierarchy, sub_params)]