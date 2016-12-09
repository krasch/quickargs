import argparse

import yaml


def parse_arguments_based_on_yaml(yaml_file):
    with open(yaml_file) as f:
        yaml_data = yaml.load(f)

    # to start with, support only a single parameter
    key = list(yaml_data.keys())[0]
    value = yaml_data[key]
    parser = argparse.ArgumentParser()
    parser.add_argument("-{}".format(key), default=value)
    args = parser.parse_args()
    return args
