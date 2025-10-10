from tomlkit import table
from dexpi.specificator.formatter import Formatter

def get_default_config():
    config = table()
    config.add('diagrams', True)
    return config

def make(*args, **kwargs):
    from .make import make
    make(*args, **kwargs)

FORMATTER = Formatter(
    'html', get_default_config, make)
