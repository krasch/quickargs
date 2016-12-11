![Build Status](https://travis-ci.org/krasch/yaml_argparse.svg)

Take a yaml config file as basis and make all parameters in the yaml file available as argparse parameters.
User can overwrite yaml config using command line arguments.

#### Example yaml config

```yaml
input:
  images: data/images
  labels: data/labels
model:
  thresholds: [0.1, 0.2, 0.5, 1.0]
logfile: output.log
```

#### Load the config and parse command line parameters


```python
import yaml
from ycli import IntegrateCommandLineArgumentsLoader

with open("config.yaml") as f:
    config = yaml.load(f, Loader=IntegrateCommandLineArgumentsLoader)

print(config)
```

#### main.py -h


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


dicts are a problem
tuples need to be passed in square brackets
none can be overwritten by anything
pairs is not supported, will have to throw exception todo
bytes is untested