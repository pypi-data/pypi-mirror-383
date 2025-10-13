import os

class BaseProgram:
    """Base template of Appication Elements"""
    config = {}

    def __init__(self, *args, **kwargs):
        self.config.update(kwargs)

    def get_config(self):
        return self.config
    
    def create(self, *args, **kwargs):
        self.config.update(kwargs)
        return self.config
    
    def add(self, *args, **kwargs):
        self.config.update(kwargs)

class Application(BaseProgram):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self, name: str, params: str, dir: str):
        os.mkdir(dir)
        return super().create(name=name, params=params, dir=dir)
    
    def test_create(self, name: str, params: str, dir: str):
        return super().create(name=name, params=params, dir=dir, projects={})
    
    def add(self, *args, **kwargs):
        return super().add(*args, **kwargs)
    
    def get_config(self):
        return super().get_config()

application = Application()