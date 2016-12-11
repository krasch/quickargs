![Build Status](https://travis-ci.org/krasch/yaml_argparse.svg)

Take a yaml config file and build a command line interface around it.

#### This config file...

```yaml
input_dir: data
logging:
    file: output.log
    level: 4
```

#### ... will give you this command line interface

```yaml
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
import ycli

with open("config.yaml") as f:
    config = yaml.load(f)
config = ycli.parse_command_line_arguments(config)
```

#### Or just supply ycli's custom yaml loader

###### main.py

```python
import yaml
import ycli

with open("config.yaml") as f:
    config = yaml.load(f, Loader=ycli.CommandLineParser)
```


#### Resulting command line interface

###### python main.py -h

```
usage: main.py [-h] [-input.images INPUT.IMAGES] [-input.labels INPUT.LABELS]
               [-logfile LOGFILE] [-model.thresholds MODEL.THRESHOLDS]

optional arguments:
  -h, --help            show this help message and exit
  -input.images INPUT.IMAGES
                        default: data/images
  -input.labels INPUT.LABELS
                        default: data/labels
  -logfile LOGFILE      default: output.log
  -model.thresholds MODEL.THRESHOLDS
                        default: [0.1, 0.2, 0.5, 1.0]

```

#### Supply some command line arguments

###### python main.py -logfile=out.log

```
{'input': {'images': 'data/images', 'labels': 'data/labels'},
 'logfile': 'out.log',
 'loglevel': 4,
 'model': {'thresholds': [0.1, 0.2, 0.5, 1.0]}}
```

#### Override nested arguments

###### python main.py -input.images=other_image_folder

```
{'input': {'images': 'other_image_folder', 'labels': 'data/labels'},
 'logfile': 'output.log',
 'model': {'thresholds': [0.1, 0.2, 0.5, 1.0]}}
```

#### Types are enforced

###### python main.py -loglevel=WARNING

```
usage: main.py [-h] [-input.images INPUT.IMAGES] [-input.labels INPUT.LABELS]
               [-logfile LOGFILE] [-loglevel LOGLEVEL]
               [-model.thresholds MODEL.THRESHOLDS]
main.py: error: argument -loglevel: invalid int value: 'WARNING'
```

#### Most yaml types, including sequences are supported

###### python main.py -model.thresholds=[0.0,1.0]

```
{'input': {'images': 'data/images', 'labels': 'data/labels'},
 'logfile': 'output.log',
 'loglevel': 4,
 'model': {'thresholds': [0.0, 1.0]}}
```

#### However, types within sequences are not enforced

#### You can even pass references to functions or classes (your own or builtins)


## Example with all supported data types


## Some gotchas

#### Tuples must be passed in square brackets

#### Instantiating of objects is not supported (but you will not get a type error)

#### The YAML pair data type is not supported

#### The YAML None type can be overwritten by anything