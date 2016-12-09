import argparse

import yaml


def parse_arguments_based_on_yaml(yaml_file):
    with open(yaml_file) as f:
        yaml_data = yaml.load(f)

    parser = argparse.ArgumentParser()
    for key, value in yaml_data.items():
        parser.add_argument("-{}".format(key), default=value)
    args = parser.parse_args()
    return args
