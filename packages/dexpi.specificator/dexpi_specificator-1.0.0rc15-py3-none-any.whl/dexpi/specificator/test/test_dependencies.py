from unittest import TestCase



import os
from pathlib import Path
import subprocess

from dexpi import specificator


def get_node_bin() -> Path:
    
    env_path = os.environ.get('NODE_BIN')
    if env_path:
        path = Path(env_path)
        if path.is_file():
            return path
        
    path = Path(specificator.__file__).parent / 'bin' / 'node' / 'node.exe'
    if path.is_file():
        return path
    
    return 'node'

        
        
class TestNode(TestCase):
    
    def test_installation(self):
        self.assertTrue(get_node_bin())
        
    def test_call(self):
        version_info = subprocess.run([get_node_bin(), '-v'], capture_output=True).stdout.decode('utf-8')
        self.assertIn(
            'v',
            version_info,
            version_info)
