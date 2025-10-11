from tomlkit import table
from dexpi.specificator.formatter import Formatter

from pnb.mcl.metamodel import standard as metamodel

Config = metamodel.AggregatedDataType('RdfConfiguration')
Config.add(metamodel.DataProperty('metamodel_namespace', str))




def get_default_config():
    config = table()
    config.add('metamodel_namespace', 'http://www.dexpi.org/temp/metamodel/')
    return config

def make(model_by_name, metadata, out_dir, config):
    from pnb.mcl.io.rdf import RdfExporter
    for name, model in model_by_name.items():
        graph = RdfExporter(model, metamodel_namespace=config['metamodel_namespace']).graph
        out_path = out_dir / f'{name}.ttl'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        graph.serialize(out_path, format='ttl')

FORMATTER = Formatter(
    'rdf', get_default_config, make)
