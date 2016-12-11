![Build Status](https://travis-ci.org/krasch/yaml_argparse.svg)

Takes a yaml config file and builds a parser for command line arguments around it. Supports nested arguments and
auto-enforces types of supplied command line parameters.

#### This config file...

```yaml
input_dir: data
logging:
    file: output.log
    level: 4
```

#### ... will give you this command line interface

```
usage: main.py [-h] [-input_dir INPUT_DIR] [-logging.file LOGGING.FILE]
               [-logging.level LOGGING.LEVEL]

optional arguments:
  -h, --help            show this help message and exit
  -input_dir INPUT_DIR  default: data
  -logging.file LOGGING.FILE
                        default: output.log
  -logging.level LOGGING.LEVEL
                        default: 4
```

#### Supply command line arguments to override values coming from the config file

###### python main.py -logging.file=other_log.txt

```
{'input_dir': 'data', 'logging': {'file': 'other_log.txt', 'level': 4}}
```

#### Enforces the types used in the yaml file

###### python main.py -logging.level=WARNING

```
usage: main.py [-h] [-input_dir INPUT_DIR] [-logging.file LOGGING.FILE]
               [-logging.level LOGGING.LEVEL]
main.py: error: argument -logging.level: invalid int value: 'WARNING'
```

###### python main.py -logging.level=0

```
{'input_dir': 'data', 'logging': {'file': 'output.log', 'level': 0}}
```
## Installation

```
pip install -r requirements.txt
```

## Usage

#### Load the yaml config and parse command line arguments

###### main.py

```python
import yaml
import quickargs

with open("config.yaml") as f:
    config = yaml.load(f)
config = quickargs.parse_args(config)
```

#### Or just supply quickargs's custom yaml loader

###### main.py

```python
import yaml
import quickargs

with open("config.yaml") as f:
    config = yaml.load(f, Loader=quickargs.YAMLLoader)
```


#### Deeply nested arguments are no problem

###### config.yaml

```yaml
key1:
  key2:
    key3:
      key4: value
```

###### python main.py -key1.key2.key3.key4=other_value

```
{'key1': {'key2': {'key3': {'key4': 'other_value'}}}}
```


#### Most yaml types, including sequences are supported

###### config.yaml

```yaml
thresholds: [0.2, 0.4, 0.6, 0.8, 1.0]
```

###### python main.py -model.thresholds='[0.0, 1.0]'

```
{'thresholds': [0.0, 0.5, 1.0]}
```

#### However, types within sequences are not enforced

###### python main.py -thresholds=[a,b,c]

```
{'thresholds': ['a', 'b', 'c']}
```

#### You can even pass references to functions or classes (your own or builtins)

###### config.yaml

```yaml
function_to_call: !!python/name:enumerate
```

###### python main.py -function_to_call=quickargs.parse_args
```
{'function_to_call': <function parse_args at 0x7f1993902b70>}
```

## Example with all supported types


## Some gotchas

#### Tuples must be passed in square brackets

#### Instantiating of objects is not supported (but you will not get a type error)

#### The YAML pair data type is not supported

#### The YAML None type can be overwritten by anything