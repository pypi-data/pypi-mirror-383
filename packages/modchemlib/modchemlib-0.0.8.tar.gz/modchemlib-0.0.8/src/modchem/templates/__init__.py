from jinja2 import FileSystemLoader, Environment
from pathlib import Path
import os

__all__ = {
    "load_app_template",
    "load_params_template",
    "load_project_main_template"
}

def load_app_template():
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    temp = env.get_template("app.py-tpl")
    render_code = temp.render({"APP_DIR": os.getenv("MODCHEM_APP_NAME")})

    with open(os.path.join(os.getcwd(), os.getenv("MODCHEM_APP_NAME"), "app.py"), "w") as file:
        file.write(render_code)

def load_params_template():
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    temp = env.get_template("params.py-tpl")
    render_code = temp.render()
    with open(os.path.join(os.getcwd(), os.getenv("MODCHEM_APP_NAME"), "params.py"), "w") as file:
        file.write(render_code)

def load_project_main_template(project_name: str):
    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    temp = env.get_template("main.py-tpl")
    render_code = temp.render()
    with open(os.path.join(os.getcwd(), project_name, "main.py"), "w") as file:
        file.write(render_code)
