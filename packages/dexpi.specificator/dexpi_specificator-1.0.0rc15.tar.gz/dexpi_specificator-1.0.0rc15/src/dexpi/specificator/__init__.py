import importlib.metadata
import pathlib

import tomlkit

THIS_DIR = pathlib.Path(__file__).parent

def _get_version() -> str:
    """
    Get the version string of dexpi.specificator.
    """
    if (pyproject_path := THIS_DIR.parent.parent.parent / 'pyproject.toml').is_file():
        with open(pyproject_path, 'rb') as pyproject_file:
            return str(tomlkit.load(pyproject_file)['project']['version'])
    else:
        version = importlib.metadata.version('dexpi.specificator')
        assert isinstance(version, str), type(version)
        return version

__version__ = _get_version()
