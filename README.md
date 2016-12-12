![Build Status](https://travis-ci.org/krasch/yaml_argparse.svg)

Takes a yaml config file and builds a parser for command line arguments around it. Supports nested arguments and
auto-enforces parameter types.

#### This config file...

```yaml
input_dir: data
logging:
    file: output.log
    level: 4
```
#### ... together with this main.py ...

```python
import yaml
import quickargs

with open("config.yaml") as f:
    config = yaml.load(f, Loader=quickargs.YAMLLoader)
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


#### Override settings using the command line

###### python main.py -logging.file=other_log.txt

#### You get your merged yaml + command line parameters in a convenient dictionary

```
# exact same output format as normal yaml.load would produce
{'input_dir': 'data', 'logging': {'file': 'other_log.txt', 'level': 4}}
```

#### The types used in the yaml file are automatically enforced

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

#### Of course it is fine to just call your program without any command line arguments

###### python main.py

```
{'key1': {'key2': {'key3': {'key4': 'value'}}}}
```

#### Most yaml types, including sequences are supported

###### config.yaml

```yaml
thresholds: [0.2, 0.4, 0.6, 0.8, 1.0]
```

###### python main.py -model.thresholds='[0.0, 0.5, 1.0]'

(take care to use ' ' around your command line arguments if they include spaces)

```
{'thresholds': [0.0, 0.5, 1.0]}
```

#### However, types within sequences are not enforced

###### config.yaml

```yaml
thresholds: [0.2, 0.4, 0.6, 0.8, 1.0]
```

###### python main.py -thresholds=[a,b,c]

```
{'thresholds': ['a', 'b', 'c']}
```

#### You can even pass references to functions or classes (your own or builtins)

###### config.yaml

```yaml
function_to_call: !!python/name:yaml.dump
```

###### python main.py -function_to_call=zip
```
{'function_to_call': <built-in function zip>}
```

## Example with all supported types

###### config.yaml

```yaml
an_int: 3
a_float: 3.0
a_bool: True
a_complex_number: 37-880j

a_date: 2016-12-11

sequences:
  a_list: [a, b, c]
  # for tuples you need to use square [] brackeds in the yaml and on the command line
  # they will still be proper tuples in the result
  a_tuple: !!python/tuple [a, b]

python:
  a_function: !!python/name:yaml.load
  a_class: !!python/name:yaml.loader.Loader
  a_module: !!python/module:contextlib
  # can be overwritten with any type
  a_none: !!python/none
```

```
python main.py -an_int=4 -a_float=2.0 -a_bool=False -a_complex_number=42-111j -a_date=2017-01-01 \
               -sequences.a_list=[c,b,c] -sequences.a_tuple=[b,a] -python.a_function=enumerate \
               -python.a_class=yaml.parser.Parser -python.a_module=yaml -python.a_none=1234
```

```
{'a_bool': False,
 'a_complex_number': '42-111j',
 'a_date': datetime.date(2017, 1, 1),
 'a_float': 2.0,
 'an_int': 4,
 'python': {'a_class': <class 'yaml.parser.Parser'>,
            'a_function': <class 'enumerate'>,
            'a_module': <module 'yaml' from ....>,
            'a_none': None},
 'sequences': {'a_list': ['c', 'b', 'c'], 'a_tuple': ('b','a')}}
```

## Un-supported types

Following types are not supported at all:
- !!python/dict (because it looks just like the rest of the yaml file)
- !!pairs

Following types are not enforced:
- !!python/object:module.cls
- !!python/object/new:module.cls
- !!python/object/apply:module.f
