import argparse
import datetime
import os
import pathlib
import sys

from lxml import etree

import tomlkit

import dexpi.specificator

from .dsl_reader import DslReader
from .formatter import get_formatter_by_name, Formatter

from pnb.mcl.metamodel import standard as metamodel

_FORMATTER_BY_NAME = get_formatter_by_name()


def make(model_src, documentation_src, formatters: list[Formatter], cache_dir) -> None:
    
    from pnb.mcl.metamodel import standard as mm

    out_dir = pathlib.Path(os.getcwd()) / '.build'
    out_dir = documentation_src.parent / '.build'
    dsl_reader = DslReader(model_src, cache_dir)
    model_set = dsl_reader.model_set

    config = {}

    for formatter in formatters:
        
        print(f'\nFormatter: {formatter.name}')
        print(out_dir.absolute())
        formatter_config = config.get(formatter, {})
        formatter_config['sphinx_project'] = str(documentation_src)
        formatter_config['index_by_path'] = dsl_reader.index_by_path
        if cache_dir is not None:
            formatter_config['cache_dir'] = str(cache_dir)
        formatter_config['out_dir'] = str(out_dir)
        
        
        

        try:
            formatter.make(model_set, formatter_config)
            print('OK')
        except Exception as error:
            raise
            print()
            print(f'*** {formatter.name} failed ***')
            print(error)
            print()


def get_argument_parser(specification_src=None, documentation_src=None):
    parser = argparse.ArgumentParser(prog='PROG')
    subparsers = parser.add_subparsers()

    make_parser = subparsers.add_parser('make', help='Make output.')
    make_parser.set_defaults(command='make')

    if not specification_src:
        make_parser.add_argument(
            'specification_src',
            metavar='spec',
            help='''
                The directory that contains the SpeciPy sources of the information model.
                Alternatively, the path of a single SpeciPy file.''')

    if not documentation_src:
        make_parser.add_argument(
            '--documentation_src',
            metavar='doc',
            help='The directory that contains a Sphinx project; required for HTML and PDF output.')

    make_parser.add_argument(
        'formatters',
        metavar='formats',
        nargs='*',
        default=None,
        choices=sorted(get_formatter_by_name()),
        help='''
            One or more formats for the output. If omitted, output for all supported formats
            is created.''')

    config_parser = subparsers.add_parser('config', help='create_config help')
    config_parser.set_defaults(command='config')
    config_parser.add_argument('out', help='file name of the config file')

    return parser


def config(out):
    out = pathlib.Path(out).absolute()

    if out.is_file():
        TODO
    elif out.exists():
        TODO

    specificator_config = tomlkit.document()
    specificator_config.add(tomlkit.comment(
        'This is an auto-generated default configuration for the DEXPI Specificator. '
        'Adapt to your needs.'))

    for formatter in _FORMATTER_BY_NAME.values():
        specificator_config.add(formatter.name, (formatter.get_default_config()))

    out.parent.mkdir(parents=True, exist_ok=True)
    # TODO: check encoding
    with out.open('w', encoding='utf-8') as file_out:
        tomlkit.dump(specificator_config, file_out)

    print(f'Default configuration written to {out}.')


def command_line(model_src=None, documentation_src=None, cache_dir=None, args=None):

    print(f'dexpi.specificator {dexpi.specificator.__version__}')
    print()

    if args is None:
        args = sys.argv[1:]

    if not args:
        print('**********************************\n'
              'Assume default command (make all).\n'
              'Run with -h to see more options.  \n'
              '**********************************')
        args = ['make']

    parser = get_argument_parser(model_src, documentation_src)
    arguments = vars(parser.parse_args(args))
    command = arguments.pop('command')

    match command:
        case 'make':

            if model_src:
                arguments['model_src'] = model_src
            if documentation_src:
                arguments['documentation_src'] = documentation_src
            if arguments['formatters']:
                arguments['formatters'] = [
                    _FORMATTER_BY_NAME[name] for name in arguments['formatters']]
            else:
                arguments['formatters'] = list(_FORMATTER_BY_NAME.values())
            arguments['cache_dir'] = cache_dir
            make(**arguments)
        case 'config':
            config(**arguments)
        case _:
            assert False, f'unknown command: {command}'

