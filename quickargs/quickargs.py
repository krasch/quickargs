import sys
import inspect
import argparse
from datetime import date, time, datetime

import yaml

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


class YAMLArgsLoader(yaml.Loader):
    """
    Convenience class for loading yaml file and parsing command line arguments in one step
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=quickargs.YAMLArgsLoader)
    """
    def get_single_data(self):
        data = super(YAMLArgsLoader, self).get_single_data()
        return merge_yaml_with_args(data)


def merge_yaml_with_args(yaml_config, argv=None):
    """
    Parse command line arguments based on a supplied yaml config.
    For each parameter in the yaml config, a command line parameter is created. The supplied command line arguments
    are parsed and merged with the yaml config. Command line arguments override yaml arguments.
    :param yaml_config: dictionary as supplied by yaml.load()
    :param argv: command line arguments, if argv is None, sys.argv will be used
    :return: dictionary with merged arguments, command line arguments override yaml arguments
    """
    # yaml files can be deeply nested. it is way more convenient to work instead with a flat dictionary
    yaml_config = flatten_dict(yaml_config)

    # argparse can not deal with nested keys -> convert keys to strings like "key.subkey.subsubkey"
    # also keep a mapping of the conversion to make it easy to convert back to nested keys
    mapping = {".".join(key): key for key, value in yaml_config.items()}
    yaml_config = {".".join(key): value for key, value in yaml_config.items()}

    # instantiate an argparse parser based on the yaml config, enforce type checking such that types of user-supplied
    # arguments must be the same as types of corresponding arguments in the yaml file
    parser = argparse.ArgumentParser()
    for key, val in sorted(yaml_config.items()):
        if len(key) == 0:
            raise ArgumentWithoutNameException()
        parser.add_argument("--{}".format(key), default=val, type=init_type_parser(val), help="default: {}".format(val))

    # parse the command line arguments and revert back from string keys to nested keys
    argv = argv or sys.argv[1:]
    cmd_config = parser.parse_args(argv)
    cmd_config = vars(cmd_config)    # vars puts command line arguments into a dict
    cmd_config = {mapping[key]: value for key, value in cmd_config.items()}

    # caller expects the original, nested config dictionary
    return unflatten_dict(cmd_config)


def init_type_parser(yaml_value):
    """
    This function uses the type of the yaml parameter to identify the correct parser for command line parsing. This
    ensures that command line parameters will have the same types as the corresponding yaml parameters.
    :param yaml_value: Any object. Type parser will be instantiated based on the type of this object
    :return: reference to parser function
    """

    # below are a bunch of functions that can be used to parse strings into specific data types
    # they are all separated into their own function with short names to get nicer output from argparse
    def yaml_bool(value):
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
        return yaml_parse_value("!!python/bytes", value)

    def yaml_python_callable(value):
        return yaml_parse_value("!!python/name", value)  # for passing module.name (functions or classes)

    def yaml_python_module(value):
        return yaml_parse_value("!!python/module", value)  # for passing package.module

    # tuples of (type_to_parse, parser) for most of the data types that can be in a yaml file
    # for most simple data types, use built-in methods, if not possible let yaml do the parsing
    # pairs, dict and bytes data types don't work, bool must be before int because isinstance(True, int) == True
    type_parsers = [(bool, yaml_bool), (int, int), (float, float), (complex, complex), (str, str), (bytes, yaml_bytes),
                    (type(None), yaml_none), (list, yaml_list), (tuple, yaml_tuple),
                    (datetime, yaml_timestamp), (date, yaml_timestamp), (time, yaml_timestamp)]
    for type_to_parse, parser in type_parsers:
        if isinstance(yaml_value, type_to_parse):
            return parser

    # some of the yaml types are specific to python2, let's be nice and handle those as well
    if sys.version_info[0] < 3:
        type_parsers = [(long, long), (unicode, unicode)]
        for type_to_parse, parser in type_parsers:
            if isinstance(yaml_value, type_to_parse):
                return parser

    # some of the types can not be detected using isinstance
    if inspect.ismodule(yaml_value):
        return yaml_python_module
    elif hasattr(type_to_parse, '__call__'):
        return yaml_python_callable

    # have not found a parser
    raise UnsupportedYAMLTypeException("Can not handle type {}".format(type(yaml_value)))


def yaml_parse_value(type_to_enforce, value):
    """
    Load off the parsing of a string into some type to yaml. This ensures that parsing is consistent between yaml
    parameters and command line parameters.
    :param type_to_enforce:
    :param value:
    :return:
    """
    try:
        if type_to_enforce in ["!!python/name", "!!python/module"]:
            yaml_data = "{}:{}".format(type_to_enforce, value)
        else:
            yaml_data = "{} {}".format(type_to_enforce, value)
        parsed = yaml.load(StringIO(yaml_data))
        return parsed
    # catch some typical errors that can happen during parsing
    # raise a ValueError instead to get nicely formatted output from argparse
    except KeyError as e:
        raise ValueError(str(e))
    except yaml.parser.ParserError as e:
        raise ValueError(str(e))
    except yaml.constructor.ConstructorError as e:
        raise ValueError(str(e))
    except AttributeError as e:
        raise ValueError(str(e))


def flatten_dict(dict_to_flatten):
    """
    Takes an arbitrarily nested dict and returns a flat dict.
    Keys of the flat dict are tuples of all keys that you need to retrieve a value from the nested dict
    E.g. input = {"key1": {"key1_1": "val11", "key1_2": {"key1_2_1": "val121"}}, "key2": "val2"}
         output = {("key1", "key1_1"): "val11", ("key1", "key1_2", "key1_2_1"): "val121", ("key2",): "val2"}
    :param dict_to_flatten:
    :return:
    """
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
    """
    Reverse of flatten_dict
    :param dict_to_unflatten:
    :return:
    """
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


class UnsupportedYAMLTypeException(Exception):
    pass


class ArgumentWithoutNameException(Exception):
    pass
