from modchem.core.project import Project
from modchem.core.params import params
from modchem.experiment.experimental import Experiment
import os
from importlib.util import spec_from_file_location, module_from_spec
import inspect
class BaseCommand:
    name=""
    description=""

    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def execute():
        pass

class CreateProjectCommand(BaseCommand):

    def __init__(self, name, description):
        super().__init__(name, description)
    
    def execute(self, title: str):
        project = Project(name=title)
        project.create()

class DeleteProjectCommand(BaseCommand):

    def __init__(self, name, description):
        super().__init__(name, description)
    
    def execute(self, title: str):
        project = Project(name=title)
        project.delete()

class ReadParamsCommand(BaseCommand):

    def __init__(self, name, description):
        super().__init__(name, description)
    
    def execute(self):
        params.update_params()
        params.get_config()

class InitProjectCommand(BaseCommand):

    def __init__(self, name, description):
        super().__init__(name, description)
    
    def execute(self, title: str):
        try:
            #load moduls on file path
            file = os.path.join(os.getcwd(), title, "main.py")
            spec = spec_from_file_location(title, file)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            all_classes = inspect.getmembers(module, inspect.isclass)
            target_class = next((cls for name, cls in all_classes if name == "TestExperiment"), None)
            if target_class:
                instance = target_class()
                instance.init()
            else:
                print("Класс TestExperiment или метод init() не найден!. Попробуйте создать файл")
        except FileExistsError:
            print("File main.py is not found")
        except FileNotFoundError:
            print("File main.py is not found")

