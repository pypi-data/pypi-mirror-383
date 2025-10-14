import os
import json
import sys
import pprint
import jsonpickle
from ruamel import yaml
from jinja2 import Environment
from backports import configparser

from echobox.tool import file
from echobox.tool import array


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def load_properties(fn, fallback=None, to_dict=True):
    if not os.path.isfile(fn):
        return fallback
    data = None
    config_string = '[DEFAULT]\n' + file.file_get_contents(fn)
    cp = configparser.ConfigParser()
    cp.optionxform = str
    cp.read_string(config_string)
    return dict(cp['DEFAULT']) if to_dict else cp['DEFAULT']


def dump_properties(data, fn):
    cp = configparser.ConfigParser()
    cp.optionxform = str
    cp['DEFAULT'] = data
    with open(fn, 'w', encoding='utf-8') as f:
        cp.write(f, space_around_delimiters=False)
    file_content = file.file_get_contents(fn)
    file_content = file_content.replace('[DEFAULT]\n', '').strip()
    file.file_put_contents(fn, file_content)


def load_json(fn, fallback=None):
    if not os.path.isfile(fn):
        return fallback
    data = None
    with open(fn, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data if data is not None else fallback


# stream could be file path or string content
def load_yaml(stream, fallback=None):
    yaml_obj = yaml.YAML(typ='safe', pure=True)
    if os.path.isfile(stream):
        with open(stream, 'r', encoding='utf-8') as f:
            data = yaml_obj.load(f)
    else:
        data = yaml_obj.load(stream)
        if data == stream:
            data = None
    return data if data is not None else fallback


def load_yaml_from_dir(dir, fallback=None):
    if not os.path.isdir(dir):
        return fallback
    file_list = file.listdir(dir)
    data = {}
    for path in file_list:
        if '.yml' not in path and '.yaml' not in path:
            continue
        data = array.merge(data, load_yaml(path, {}))
    return data


def load_yaml_config(config_file, config_section=None, extra_kvs=None):
    config = load_yaml(config_file, {})
    if config_section is not None:
        key_list = config_section.split('.')
        for sub_key in key_list:
            if sub_key not in config:
                raise Exception('Can not find config section for sub key:' + sub_key)
            config = config[sub_key]

    if extra_kvs is not None:
        config.update(extra_kvs)
    return config


def dump_json(data, fn, **kwargs):
    with open(fn, 'w', encoding='utf-8') as outfile:
        json_str = jsonpickle.encode(data)  # for data contains object
        data = json.loads(json_str)
        json.dump(data, outfile, **kwargs)


def pjson(data):
    try:
        return json.dumps(data, indent=2, sort_keys=True)
    except:
        return pprint.pformat(object=data, indent=2, sort_dicts=True)  # for data contains object


def pyaml(data):
    yaml.Dumper.ignore_aliases = lambda *args: True
    return yaml.safe_dump(data, default_flow_style=False)


# TODO: should be dump_yaml(data, fn)
def dump_yaml(fn, data):
    yaml_obj = yaml.YAML(typ='safe', pure=True)
    with open(fn, 'w', encoding='utf-8') as outfile:
        yaml_obj.dump(data, outfile)


def json_to_yaml(src, out):
    data = load_json(src)
    dump_yaml(data, out)

def python_executable_path():
    import sys
    return sys.executable
