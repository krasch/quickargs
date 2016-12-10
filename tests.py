from tempfile import NamedTemporaryFile
import sys

import yaml
from nose.tools import assert_dict_equal, raises

from yaml_argparse import parse_arguments_based_on_yaml, unflatten_dict, flatten_dict


def create_yaml_and_parse_arguments(yaml_params, command_line_params):
    sys.argv[1:] = command_line_params    # pretend params come directly from the command line

    with NamedTemporaryFile("w") as temp_file:
        yaml.dump(yaml_params, temp_file, default_flow_style=False)
        config = parse_arguments_based_on_yaml(temp_file.name)

    return config


@raises(SystemExit)
def test_illegal_commmandline_param():
    yaml_params = {"key1": "yaml_value_key1"}
    command_line_params = ["-not_existing=cmd_value"]
    create_yaml_and_parse_arguments(yaml_params, command_line_params)


def test_one_string_no_overwrite():
    yaml_params = {"key1": "yaml_value_key1"}
    command_line_params = []
    expected = {"key1": "yaml_value_key1"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_one_string_overwrite():
    yaml_params = {"key1": "yaml_value_key1"}
    command_line_params = ["-key1=cmd_value_key1"]
    expected = {"key1": "cmd_value_key1"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_one_string_overwrite_same_value():
    yaml_params = {"key1": "yaml_value_key1"}
    command_line_params = ["-key1=yaml_value_key1"]
    expected = {"key1": "yaml_value_key1"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_multiple_strings_no_overwrite():
    yaml_params = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}
    command_line_params = []
    expected = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_multiple_strings_one_overwrite():
    yaml_params = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}
    command_line_params = ["-key2=cmd_value_key2"]
    expected = {"key1": "yaml_value_key1", "key2": "cmd_value_key2", "key3": "yaml_value_key3"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_multiple_strings_two_overwrite():
    yaml_params = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}
    command_line_params = ["-key2=cmd_value_key2", "-key3=cmd_value_key3"]
    expected = {"key1": "yaml_value_key1", "key2": "cmd_value_key2", "key3": "cmd_value_key3"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_multiple_strings_all_overwrite():
    yaml_params = {"key1": "yaml_value_key1", "key2": "yaml_value_key2", "key3": "yaml_value_key3"}
    command_line_params = ["-key1=cmd_value_key1", "-key2=cmd_value_key2", "-key3=cmd_value_key3"]
    expected = {"key1": "cmd_value_key1", "key2": "cmd_value_key2", "key3": "cmd_value_key3"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_nested_no_overwrite():
    yaml_params = {"key1": {"key1_1": "yaml_value_key1_1"}}
    command_line_params = []
    expected = {"key1": {"key1_1": "yaml_value_key1_1"}}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_nested_overwrite():
    yaml_params = {"key1": {"key1_1": "yaml_value_key1_1"}}
    command_line_params = ["-key1.key1_1=cmd_value_key1_1"]
    expected = {"key1": {"key1_1": "cmd_value_key1_1"}}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_nested_overwrite_deep():
    yaml_params = {"key1":
                       {"key1_1":
                            {"key1_1_1": "yaml_value_key1_1_1",
                             "key1_1_2": "yaml_value_key1_1_2"},
                        "key1_2": "yaml_value_key1_2"},
                   "key2": "yaml_value_key2"}
    command_line_params = ["-key1.key1_1.key1_1_2=cmd_value_key1_1_2", "-key2=cmd_value_key2"]
    expected = {"key1":
                    {"key1_1":
                         {"key1_1_1": "yaml_value_key1_1_1",
                          "key1_1_2": "cmd_value_key1_1_2"},
                     "key1_2": "yaml_value_key1_2"},
                "key2": "cmd_value_key2"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_int():
    yaml_params = {"key1": 123}
    command_line_params = ["-key1=234"]
    expected = {"key1": 234}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_flatten_dict_empty():
    dict_to_flatten = {}
    expected = {}

    actual = flatten_dict(dict_to_flatten)
    assert_dict_equal(expected, actual)


def test_flatten_dict_shallow():
    dict_to_flatten = {"key1": "val1", "key2": "val2"}
    expected = {("key1",): "val1", ("key2",): "val2"}

    actual = flatten_dict(dict_to_flatten)
    assert_dict_equal(expected, actual)


def test_flatten_dict_nested():
    dict_to_flatten = {"key1":
                           {"key1_1": "val11",
                            "key1_2":
                                {"key1_2_1": "val121"}},
                       "key2": "val2"}
    expected = {("key1", "key1_1"): "val11",
                ("key1", "key1_2", "key1_2_1"): "val121",
                ("key2",): "val2"}

    actual = flatten_dict(dict_to_flatten)
    assert_dict_equal(expected, actual)


def test_unflatten_dict_empty():
    dict_to_unflatten = {}
    expected = {}

    actual = unflatten_dict(dict_to_unflatten)
    assert_dict_equal(expected, actual)


def test_unflatten_dict_shallow():
    dict_to_unflatten = {("key1",): "val1", ("key2",): "val2"}
    expected = {"key1": "val1", "key2": "val2"}

    actual = unflatten_dict(dict_to_unflatten)
    assert_dict_equal(expected, actual)


def test_unflatten_dict_nested():
    dict_to_unflatten = {("key1", "key1_1"): "val11",
                         ("key1", "key1_2", "key1_2_1"): "val121",
                         ("key2",): "val2"}
    expected = {"key1":
                    {"key1_1": "val11",
                     "key1_2":
                         {"key1_2_1": "val121"}},
                "key2": "val2"}

    actual = unflatten_dict(dict_to_unflatten)
    assert_dict_equal(expected, actual)
