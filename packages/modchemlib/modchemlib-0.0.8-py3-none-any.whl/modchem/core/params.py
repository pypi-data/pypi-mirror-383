from modchem.core.app import BaseProgram
import os
import re

class AppParams(BaseProgram):
    params = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_config(self):
        print(self.params)
        return self.params
    
    def update_params(self, *args, **kwargs):
        file = os.path.join(os.getcwd(), "params.py")
        with open(file, 'r') as f:
            file_content = f.read()
            matches = re.findall(r'(\w+)\s*=\s*(.+)', file_content)
            for keys, variables in matches:
                self.params.setdefault(keys, variables)
            f.close()

params = AppParams()