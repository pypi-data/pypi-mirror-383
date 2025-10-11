from __future__ import annotations 

import importlib
import pathlib
import typing as T

if T.TYPE_CHECKING:
    from pnb.mcl.metamodel import standard as metamodel

class Formatter:
    def __init__(self, name, get_default_config, make):
        self.name = name
        self._get_default_config = get_default_config
        self._make = make
        
    def get_default_config(self):
        return self._get_default_config()
    
    def make(self, model_set: metamodel.ModelSet, config: dict):
        actual_config = self.get_default_config()
        actual_config.update(config or {})
        actual_config['out_dir'] = str(pathlib.Path(actual_config['out_dir']) / self.name)
        self._make(model_set, actual_config)

    
_FORMATTER_BY_NAME = None
    
# TODO: rename
def get_formatter_by_name():
    global _FORMATTER_BY_NAME
    if _FORMATTER_BY_NAME is None:
        temp_retval = {}
        from . import formatters
        formatters_dir = pathlib.Path(formatters.__path__[0])
        for dir_entry in formatters_dir.iterdir():
            if dir_entry.is_dir():
                module_name = dir_entry.name
            elif dir_entry.is_file() and dir_entry.suffixes == ['.py']:
                module_name = dir_entry.name[:-3]
            else:
                continue
            module = importlib.import_module(f'.{module_name}', formatters.__name__)
            formatter = getattr(module, 'FORMATTER', None)
            if formatter:
                assert isinstance(formatter, Formatter)
                assert formatter.name not in temp_retval
                temp_retval[formatter.name] = formatter
        _FORMATTER_BY_NAME = temp_retval
    return _FORMATTER_BY_NAME
