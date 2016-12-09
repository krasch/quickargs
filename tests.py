from tempfile import NamedTemporaryFile
import sys

import yaml
from nose.tools import assert_dict_equal, raises

from yaml_argparse import parse_arguments_based_on_yaml


def create_yaml_and_parse_arguments(yaml_params, command_line_params):
    command_line_params = ["-{}={}".format(key, value) for key, value in command_line_params.items()]
    sys.argv[1:] = command_line_params    # pretend params come directly from the command line

    with NamedTemporaryFile("w") as temp_file:
        yaml.dump(yaml_params, temp_file, default_flow_style=False)
        args = parse_arguments_based_on_yaml(temp_file.name)

    args_as_dict = vars(args)
    return args_as_dict


def test_one_string_no_overwrite():
    yaml_params = {"test": "yaml_value"}
    command_line_params = {}
    expected = {"test": "yaml_value"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_one_string_overwrite():
    yaml_params = {"test": "yaml_value"}
    command_line_params = {"test": "cmd_value"}
    expected = {"test": "cmd_value"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_one_string_overwrite_same_value():
    yaml_params = {"test": "yaml_value"}
    command_line_params = {"test": "yaml_value"}
    expected = {"test": "yaml_value"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


@raises(SystemExit)
def test_illegal_commmandline_param():
    yaml_params = {"test": "yaml_value"}
    command_line_params = {"not_existing": "cmd_value"}
    create_yaml_and_parse_arguments(yaml_params, command_line_params)
