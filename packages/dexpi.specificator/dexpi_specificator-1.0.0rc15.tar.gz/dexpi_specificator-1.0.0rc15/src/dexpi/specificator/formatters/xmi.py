import pathlib

from lxml import etree
from tomlkit import table

from pnb.mcl.metamodel import standard as metamodel

from dexpi.specificator.formatter import Formatter


def get_default_config():
    config = table()
    config.add('pretty_print', True)
    return config

def make(model_set: metamodel.ModelSet, config: dict):
    out_dir = pathlib.Path(config['out_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)    

    from pnb.mcl.io.xmi import XmiWriter, XmiConfiguration
    out_dir.mkdir(parents=True, exist_ok=True)
    
    from pnb.mcl.metamodel.standard import ModelSet

    #  TODO: file name from config
    etree.ElementTree(XmiWriter(model_set).root).write(
        out_dir / 'Dexpi.xmi', encoding='utf-8', pretty_print=config['pretty_print'])

    xmi_config = XmiConfiguration(primitive_type_prefix='Primitive')
    etree.ElementTree(XmiWriter(model_set, xmi_config).root).write(
        out_dir / 'Dexpi for Modelio.xmi', encoding='utf-8', pretty_print=config['pretty_print'])

FORMATTER = Formatter(
    'xmi', get_default_config, make)
