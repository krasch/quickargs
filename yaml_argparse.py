import sys
import argparse
from datetime import datetime

import yaml

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


def yaml_parse_value(type_to_enforce, value):
    try:
        parsed = yaml.load(StringIO("{} {}".format(type_to_enforce, value)))
        return parsed
    # catch some typical errors that can happen during parsing
    # raise a ValueError instead to get nicely formatted output from argparse
    except KeyError:
        raise ValueError()
    except yaml.parser.ParserError:
        raise ValueError()
    except yaml.constructor.ConstructorError:
        raise ValueError()
    except AttributeError:
        raise ValueError()


def init_type_parser(yaml_value):
    """
    Type of command line argument should match the type of same argument in yaml file.
    This function uses the type of the yaml argument to identify the correct parser for command line parsing.
    :param yaml_value:
    :return:
    """

    # below are a bunch of functions that can be used to parse strings into specific data types
    # they are all separated into their own function with short names to get nicer output from argparse
    def yaml_bool(value):
        print(yaml_parse_value("!!bool", value))
        return yaml_parse_value("!!bool", value)

    def yaml_list(value):
        return yaml_parse_value("!!python/list", value)

    def yaml_tuple(value):
        return yaml_parse_value("!!python/tuple", value)

    def yaml_none(value):
        return yaml_parse_value("!!python/none", value)

    def yaml_timestamp(value):
        return yaml_parse_value("!!timestamp", value)

    def yaml_bytes(value):
        return yaml_parse_value("!!python", value)

    # list of tuples of (type_to_parse, parser) for most of the data types that can be in a yaml file
    # for most simple data types, use built-in methods, if not possible let yaml do the parsing
    # pairs and dict are generally not supported by this library, bytes can not be supplied as a command line argument
    type_parsers = [(bool, yaml_bool), (int, int), (float, float), (complex, complex), (str, str),
                    (type(None), yaml_none), (datetime, yaml_timestamp), (list, yaml_list), (tuple, yaml_tuple)]

    for type_to_parse, parser in type_parsers:
        if isinstance(yaml_value, type_to_parse):
            return parser

    # some of the yaml types are specific to python2, let's be nice and handle those as well
    if sys.version_info[0] < 3:
        type_parsers = [(long, long), (unicode, unicode)]
        for type_to_parse, parser in type_parsers:
            if isinstance(yaml_value, type_to_parse):
                return parser

    # have not found a parser
    raise Exception("Can not handle type {}".format(type(yaml_value)))


def make_parser(config):
    parser = argparse.ArgumentParser()
    for key, value in config.items():
        parser.add_argument("-{}".format(key), default=value, type=init_type_parser(value))
    return parser


def parse_command_line_arguments(config):
    # argparse can not deal with nested keys -> convert keys to strings like "key.subkey.subsubkey"
    # also keep a mapping of the conversion to make it easy to convert back to nested keys
    mapping = {".".join(key): key for key, value in config.items()}
    config = {".".join(key): value for key, value in config.items()}

    # parse the command line arguments
    parser = make_parser(config)
    args = parser.parse_args()
    args_dict = vars(args)

    # revert back from string keys to nested keys
    return {mapping[key]: value for key, value in args_dict.items()}


def parse_arguments_based_on_yaml(yaml_file):
    # read the yaml file, this will be the base config
    # for each parameter in the base config a command line argument will be created to allow overwriting the parameter
    with open(yaml_file) as f:
        config = yaml.load(f)

    # yaml files can be deeply nested. it is way more convenient to work instead with a flat dictionary
    config_flat = flatten_dict(config)

    # parse command line arguments and overwrite the yaml configuration with command line parameters
    command_line_arguments = parse_command_line_arguments(config_flat)
    for key, value in command_line_arguments.items():
        config_flat[key] = value

    # caller expects the original, nested config dictionary
    config = unflatten_dict(config_flat)
    return config


def flatten_dict(dict_to_flatten):
    def merge_dicts(dicts_to_merge):
        return {key: value for to_merge in dicts_to_merge for key, value in to_merge.items()}

    def recursive_flatten(current_key_hierarchy, value):
        if isinstance(value, dict):
            sub_dicts = [recursive_flatten(current_key_hierarchy + [key], val) for key, val in value.items()]
            return merge_dicts(sub_dicts)
        else:
            return {tuple(current_key_hierarchy): value}

    return recursive_flatten([], dict_to_flatten)


def unflatten_dict(dict_to_unflatten):
    def recursive_set_value(sub_dict, keys, value):
        if len(keys) == 1:
            sub_dict[keys[0]] = value
        else:
            if keys[0] not in sub_dict:
                sub_dict[keys[0]] = {}
            recursive_set_value(sub_dict[keys[0]], keys[1:], value)

    unflattened = {}
    for key_hierarchy, value in dict_to_unflatten.items():
        recursive_set_value(unflattened, key_hierarchy, value)

    return unflattened
