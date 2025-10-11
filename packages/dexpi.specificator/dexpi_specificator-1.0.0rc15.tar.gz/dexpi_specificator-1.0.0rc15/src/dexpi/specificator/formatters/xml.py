import pathlib

from tomlkit import table
from lxml import etree

from dexpi.specificator.formatter import Formatter

from pnb.mcl.metamodel import standard as metamodel
from pnb.mcl.io.xml import XmlExporter


def get_default_config():
    config = table()
    config.add('pretty_print', True)
    return config

def make(model_set, config):
    out_dir = pathlib.Path(config['out_dir'])
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for model in model_set:
        exporter = XmlExporter(
            model,
            model_set)
        xml = exporter.xml
        out_path = out_dir / f'{model.name}.xml'
        etree.ElementTree(xml).write(
            out_path, encoding='utf-8', pretty_print=config['pretty_print'])

FORMATTER = Formatter(
    'xml', get_default_config, make)
