import unittest
from modchem.core.app import application

class TestAppMethods(unittest.TestCase):
    def test_get_app_config(self):
        _test_result = {"name": "example", "params": "params.py", "dir":"./example", "projects": {}}
        self.assertEqual(application.test_create(name="example", params="params.py", dir="./example"), _test_result)

