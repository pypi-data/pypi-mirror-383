import sys, os
from argparse import ArgumentParser
from pathlib import Path
class ExecuteEnvironment:
    """Класс инициализации виртуальной среды"""
    args = ""
    commands = []
    def __init__(self, args):
        self.args = args
        
    def initialize(self):
        self.execute(self.args)

    def execute(self, dir: str):
        os.environ["MODCHEM_INIT"] = os.path.join(os.getcwd(), dir)
        try:
            Path(os.path.join(os.getcwd(), dir)).mkdir()
        except FileExistsError:
            sys.stderr.write(f"Путь {os.getenv("MODCHEM_INIT")} уже занят")

def execute_command_line():
    print(sys.argv)

def execute_experiment_environment():
    parser = ArgumentParser(description="Initial Experiment Environment")
    parser.add_argument("project_name", help="Environment name")
    argv = parser.parse_args()
    execute = ExecuteEnvironment(args=argv._get_kwargs()[0][1])
    execute.initialize()