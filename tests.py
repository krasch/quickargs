from tempfile import NamedTemporaryFile
import sys
from datetime import datetime, timedelta
from contextlib import contextmanager

import yaml
from nose.tools import assert_dict_equal, raises

from yaml_argparse import parse_command_line_arguments, flatten_dict, unflatten_dict, UnsupportedYAMLTypeException, \
    IntegrateCommandLineArgumentsLoader

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

###################################################################
# convenience methods for running tests
###################################################################


@contextmanager
def temp_yaml_file(yaml_config):
    with NamedTemporaryFile("w") as temp_file:
        if isinstance(yaml_config, str):
            with open(temp_file.name, "w") as f:
                f.write(yaml_config)
        else:
            yaml.dump(yaml_config, temp_file, default_flow_style=False)
        yield temp_file.name


@contextmanager
def set_sys_argv(command_line_params):
    """
    set and most IMPORTANTLY unset command line parameters, otherwise they can still be set for the next test
    :param command_line_params:
    :return:
    """
    sys.argv[1:] = command_line_params
    yield
    sys.argv[1:] = []


def create_yaml_and_parse_arguments(yaml_config, command_line_params):
    # dumping and loading just to make sure to pass it through yaml once
    with temp_yaml_file(yaml_config) as temp_file:
        with open(temp_file) as f:
            yaml_config = yaml.load(f)

    with set_sys_argv(command_line_params):
        config = parse_command_line_arguments(yaml_config)
    return config


####################################################################################
# Tests for string parameters, in yaml files of various complexity / nestedness
####################################################################################
"""
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


#####################################################
# Tests for types
######################################################


def test_int():
    yaml_params = {"key1": 123}
    command_line_params = ["-key1=234"]
    expected = {"key1": 234}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


@raises(SystemExit)
def test_int_command_line_type_wrong():
    yaml_params = {"key1": 123}
    command_line_params = ["-key1=hallo"]

    create_yaml_and_parse_arguments(yaml_params, command_line_params)


def test_long_py2_only():
    if sys.version_info[0] < 3:
        yaml_params = {"key1": long(123)}
        command_line_params = ["-key1=234"]
        expected = {"key1": long(234)}

        actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
        assert_dict_equal(expected, actual)


def test_long_command_line_type_wrong_py2_only():
    if sys.version_info[0] < 3:
        yaml_params = {"key1": long(123)}
        command_line_params = ["-key1=hallo"]
        try:
            create_yaml_and_parse_arguments(yaml_params, command_line_params)
        except SystemExit:
            return
        assert False, "Did not raise SystemExit"


def test_float():
    yaml_params = {"key1": 123.0}
    command_line_params = ["-key1=234.0"]
    expected = {"key1": 234.0}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


@raises(SystemExit)
def test_float_command_line_type_wrong():
    yaml_params = {"key1": 123.0}
    command_line_params = ["-key1=hallo"]

    create_yaml_and_parse_arguments(yaml_params, command_line_params)


def test_complex():
    yaml_params = {"key1": 37-880j}
    command_line_params = ["-key1=44-880j"]
    expected = {"key1": 44-880j}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


@raises(SystemExit)
def test_float_command_line_type_wrong():
    yaml_params = {"key1": 37-880j}
    command_line_params = ["-key1=hallo"]

    create_yaml_and_parse_arguments(yaml_params, command_line_params)


def test_bool():
    yaml_params = {"key1": True}
    command_line_params = ["-key1=False"]
    expected = {"key1": False}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_bool_alternative_false():
    yaml_params = {"key1": True}
    command_line_params = ["-key1=No"]
    expected = {"key1": False}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


@raises(SystemExit)
def test_bool_command_line_type_wrong():
    yaml_params = {"key1": True}
    command_line_params = ["-key1=hallo"]

    create_yaml_and_parse_arguments(yaml_params, command_line_params)


def test_none():
    yaml_params = {"key1": None}
    command_line_params = ["-key1=None"]
    expected = {"key1": None}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_none_overwrite():
    yaml_params = {"key1": None}
    command_line_params = ["-key1=value"]
    expected = {"key1": None}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_timestamp():
    time_old = datetime.now()
    time_new = time_old + timedelta(hours=1)

    yaml_params = {"key1": time_old}
    command_line_params = ["-key1={}".format(time_new)]
    expected = {"key1": time_new}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


@raises(SystemExit)
def test_timestamp_command_line_type_wrong():
    yaml_params = {"key1": datetime.now()}
    command_line_params = ["-key1=hallo"]

    create_yaml_and_parse_arguments(yaml_params, command_line_params)


@raises(UnsupportedYAMLTypeException)
def test_bytes_py3_only():
    if sys.version_info[0] >= 3:
        yaml_params = {"key1": b"value"}
        command_line_params = ["-key1=b'123'"]
        create_yaml_and_parse_arguments(yaml_params, command_line_params)
    else:
        # always succeed for python 2
        raise UnsupportedYAMLTypeException()


def test_unicode():
    yaml_params = {"key1": u"test"}
    command_line_params = ["-key1=234"]
    expected = {"key1": "234"}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_list_of_strings():
    yaml_params = {"key1": ['a', 'b', 'c']}
    command_line_params = ["-key1=['x', 'y', 'z']"]
    expected = {"key1": ["x", "y", "z"]}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_list_of_ints():
    yaml_params = {"key1": [0, 1, 2]}
    command_line_params = ["-key1=[2, 4]"]
    expected = {"key1": [2, 4]}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_list_of_mixed_types():
    # warning: can not enforce anything about the types in a list
    yaml_params = {"key1": [0, "a", 2]}
    command_line_params = ["-key1=[b, 4, True]"]
    expected = {"key1": ['b', 4, True]}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_empty_list_in_cmd():
    yaml_params = {"key1": [0, 1, 2]}
    command_line_params = ["-key1=[]"]
    expected = {"key1": []}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_empty_list_in_yaml():
    yaml_params = {"key1": []}
    command_line_params = ["-key1=[0, 1, 2]"]
    expected = {"key1": [0, 1, 2]}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


@raises(SystemExit)
def test_list_command_line_type_wrong():
    yaml_params = {"key1": [0, 1, 2]}
    command_line_params = ["-key1=hallo"]

    create_yaml_and_parse_arguments(yaml_params, command_line_params)


def test_tuple_of_strings():
    yaml_params = {"key1": ('a', 'b')}
    command_line_params = ["-key1=['c', 'd']"]
    expected = {"key1": ("c", "d")}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_tuple_of_ints():
    yaml_params = {"key1": (0, 1, 2)}
    command_line_params = ["-key1=[4, 5]"]
    expected = {"key1": (4, 5)}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_tuple_of_mixed_types():
    # warning: can not enforce anything about the types in a tuple
    yaml_params = {"key1": ('a', 'b')}
    command_line_params = ["-key1=[0, 'd']"]
    expected = {"key1": (0, "d")}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_empty_tuple_in_cmd():
    yaml_params = {"key1": (0, 1, 2)}
    command_line_params = ["-key1=[]"]
    expected = {"key1": ()}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_empty_tuple_in_yaml():
    yaml_params = {"key1": ()}
    command_line_params = ["-key1=[0, 1, 2]"]
    expected = {"key1": (0, 1, 2)}

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


@raises(SystemExit)
def test_tuple_command_line_type_wrong():
    yaml_params = {"key1": (0, 1, 2)}
    command_line_params = ["-key1=hallo"]

    create_yaml_and_parse_arguments(yaml_params, command_line_params)
"""


def test_function():
    yaml_params = "key1: !!python/name:tests.functionA"
    command_line_params = ["-key1=tests.functionB"]
    expected = functionB

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)["key1"]
    assert actual == expected


@raises(SystemExit)
def test_function_not_exist():
    yaml_params = "key1: !!python/name:tests.functionA"
    command_line_params = ["-key1=tests.not_existing"]
    create_yaml_and_parse_arguments(yaml_params, command_line_params)


def test_class():
    yaml_params = "key1: !!python/name:tests.ClassA"
    command_line_params = ["-key1=tests.ClassB"]
    expected = ClassB

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)["key1"]
    assert actual == expected


@raises(SystemExit)
def test_class_not_exist():
    yaml_params = "key1: !!python/name:tests.ClassA"
    command_line_params = ["-key1=tests.not_existing"]
    expected = ClassB

    actual = create_yaml_and_parse_arguments(yaml_params, command_line_params)["key1"]
    assert actual == expected
    

"""
#############################################
# test integration with yaml
############################################

# pass a list of arguments, instead of taking the ones from sys
def test_with_supplied_arguments():
    yaml_params = {"key1": "yaml_value_key1", "key2": {"key2_1": 21, "key2_2": 22}}
    command_line_params = ["-key1=cmd_value_key1", "-key2.key2_2=7"]
    expected = {"key1": "cmd_value_key1", "key2": {"key2_1": 21, "key2_2": 7}}

    # dumping and loading just to make sure to pass it through yaml once
    with temp_yaml_file(yaml_params) as temp_file:
        with open(temp_file) as f:
            yaml_params = yaml.load(f)

    actual = parse_command_line_arguments(yaml_params, command_line_params)
    assert_dict_equal(expected, actual)


def test_loader_from_file():
    yaml_params = {"key1": "yaml_value_key1", "key2": {"key2_1": 21, "key2_2": 22}}
    command_line_params = ["-key1=cmd_value_key1", "-key2.key2_2=7"]
    expected = {"key1": "cmd_value_key1", "key2": {"key2_1": 21, "key2_2": 7}}

    with temp_yaml_file(yaml_params) as temp_file:
        with open(temp_file) as f:
            with set_sys_argv(command_line_params):
                actual = yaml.load(f, Loader=IntegrateCommandLineArgumentsLoader)

    assert_dict_equal(expected, actual)


def test_loader_from_stringio():
    yaml_params = {"key1": "yaml_value_key1", "key2": {"key2_1": 21, "key2_2": 22}}
    command_line_params = ["-key1=cmd_value_key1", "-key2.key2_2=7"]
    expected = {"key1": "cmd_value_key1", "key2": {"key2_1": 21, "key2_2": 7}}

    with temp_yaml_file(yaml_params) as temp_file:
        with open(temp_file) as f:
            stream = StringIO(f.read())
            with set_sys_argv(command_line_params):
                actual = yaml.load(stream, Loader=IntegrateCommandLineArgumentsLoader)

    assert_dict_equal(expected, actual)


#############################################
# Tests for some of the utility functions
############################################

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
"""

##########################################################
# References that are needed for some of the tests
#########################################################


class ClassA:
    pass


class ClassB:
    pass


def functionA():
    pass


def functionB():
    pass