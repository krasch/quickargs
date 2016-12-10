![Build Status](https://travis-ci.org/krasch/yaml_argparse.svg)

Take a yaml config file as basis and make all parameters in the yaml file available as argparse parameters.
User can overwrite yaml config using command line arguments.


does not enforce types within complex types

dicts are a problem
tuples need to be passed in square brackets
none can not be overwritten
pairs is not supported, will have to throw exception todo
bytes is untested