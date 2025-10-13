class BaseCommand:
    
    name=""
    description=""

    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def dict_parser(self) -> dict:
        return self.__dict__

class ExecuteCommand(BaseCommand):

    def __init__(self, name, description):
        super().__init__(name, description)

