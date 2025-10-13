class Application:
    app_name = ""
    app_params = ""
    project_list = []

    def __init__(self):
        pass

    def set_app(self, name: str, params: str):
        self.app_name = name
        self.app_params = params

def register_app(name: str, params: str):
    app = Application()
    app.set_app(name=name, params=params)