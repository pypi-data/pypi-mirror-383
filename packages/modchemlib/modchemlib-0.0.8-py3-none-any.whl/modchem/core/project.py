import os
import shutil
from modchem.core.app import BaseProgram
from modchem.templates import load_project_main_template

class Project(BaseProgram):
    name: str
    body: dict
    
    def __init__(self, name, *args, **kwargs):
        self.name = name

    def get_config(self):
        return self.__dict__
    
    def test_create(self):
        if self.name is None:
            return ValueError("Project hasn't name")
        
    def create(self):
        if self.name is None:
            return ValueError("Project hasn't name")
        os.mkdir(os.path.join(os.getcwd(), self.name))
        load_project_main_template(project_name=self.name)
    
    def delete(self):
        shutil.rmtree(os.path.join(os.getcwd(), self.name))
        
