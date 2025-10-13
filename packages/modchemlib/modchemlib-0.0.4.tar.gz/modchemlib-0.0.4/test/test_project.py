import unittest
from modchem.core.project import Project

class TestProjectMethods(unittest.TestCase):

    def test_create_project(self):
        project = Project(name="Testing")
        self.assertEqual(project.get_config(), {'name': 'Testing'})