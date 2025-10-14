import shutil

from src.common.config import get_easyfed_config_from_yaml
from src.common.errors import InvalidStateError
from src.common.project import EasyFedProject
from src.common.state import Dirty


def clean(path: str):
    configuration = get_easyfed_config_from_yaml(path=path)
    easyfed_project = EasyFedProject(config=configuration)
    easyfed_state = easyfed_project.project_state
    match easyfed_state.state:
        case Dirty():
            shutil.rmtree(easyfed_project.project_folder)
            pass
        case _:
            raise InvalidStateError()
