from tempfile import NamedTemporaryFile
import sys

import yaml
from nose.tools import assert_dict_equal, raises

from yaml_argparse import parse_arguments_based_on_yaml


def format_params_for_command_line(params):
    """
    Take an arbitrarily nested dict and make command line parameters like key1.subkey1_1.subkey_1_1 = some_value
    :param params: dictionary of parameters, can be arbitrarily nested
    :return: list of command line parameters
    """

    def flatten_dict(key_hierarchy, params_for_key_hierarchy):
        if isinstance(params_for_key_hierarchy, dict):
            sub_result_nested = [flatten_dict(key_hierarchy+[key], val) for key, val in params_for_key_hierarchy.items()]
            sub_result_flattened = [s for sub in sub_result_nested for s in sub]
            return sub_result_flattened
        else:
            return [(key_hierarchy, params_for_key_hierarchy)]

    flattened = flatten_dict([], params)
    flattened = ["-{}={}".format(".".join(key), value) for key, value in flattened]
    return flattened


def create_yaml_and_parse_arguments(yaml_params, command_line_params):
    command_line_params = format_params_for_command_line(command_line_params)
    sys.argv[1:] = command_line_params    # pretend params come directly from the command line

    with NamedTemporaryFile("w") as temp_file:
        yaml.dump(yaml_params, temp_file, default_flow_style=False)
        args = parse_arguments_based_on_yaml(temp_file.name)

    args_as_dict = vars(args)
    return args_as_dict

@raises(SystemExit)
def test_illegal_commmandline_param():
    yaml_params = {"key1": "yaml_value_key1"}
    command_line_params = {"not_existing": "cmd_value"}
    create_yaml_and_parse_arguments(yaml_params, command_line_params)


def test_one_string_no_overwrite():
    yaml_params = {"key1": "yaml_value_key1"}
    command_line_params = {}
    expected = {"key1": "yaml_value_key1"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_one_string_overwrite():
    yaml_params = {"key1": "yaml_value_key1"}
    command_line_params = {"key1": "cmd_value_key1"}
    expected = {"key1": "cmd_value_key1"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_one_string_overwrite_same_value():
    yaml_params = {"key1": "yaml_value_key1"}
    command_line_params = {"key1": "yaml_value_key1"}
    expected = {"key1": "yaml_value_key1"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_multiple_strings_no_overwrite():
    yaml_params = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}
    command_line_params = {}
    expected = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_multiple_strings_one_overwrite():
    yaml_params = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}
    command_line_params = {"key2": "cmd_value_key2"}
    expected = {"key1": "yaml_value_key1", "key2": "cmd_value_key2", "key3": "yaml_value_key3"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_multiple_strings_two_overwrite():
    yaml_params = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}
    command_line_params = {"key2": "cmd_value_key2", "key3": "cmd_value_key3"}
    expected = {"key1": "yaml_value_key1", "key2": "cmd_value_key2", "key3": "cmd_value_key3"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_multiple_strings_all_overwrite():
    yaml_params = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}
    command_line_params = {"key1": "cmd_value_key1", "key2": "cmd_value_key2", "key3": "cmd_value_key3"}
    expected = {"key1": "cmd_value_key1", "key2": "cmd_value_key2", "key3": "cmd_value_key3"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_nested_no_overwrite():
    yaml_params = {"key1": {"subkey1": "yaml_value_subkey1"}}
    command_line_params = {}
    expected = {"key1": {"subkey1": "yaml_value_subkey1"}}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)

"""
def test_nested_overwrite_deep():
    yaml_params = {"key1": {"subkey1": "yaml_value_subkey1"}}
    command_line_params = {"key1": {"key1_1": {"key1_1_1": "cmd_value_key1_1_1","key1_1_2": "cmd_value_key1_1_2"}, "key1_2": "cmd_value_key1_2"}}
    expected = {"key1": {"subkey1": "cmd_value_subkey1"}}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)
"""