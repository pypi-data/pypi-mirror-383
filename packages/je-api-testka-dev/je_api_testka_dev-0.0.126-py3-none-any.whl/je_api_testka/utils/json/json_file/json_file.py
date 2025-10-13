import json
from pathlib import Path
from threading import Lock
from typing import Dict

from je_api_testka.utils.exception.exception_tags import cant_find_json_error
from je_api_testka.utils.exception.exception_tags import cant_save_json_error
from je_api_testka.utils.exception.exceptions import APITesterJsonException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

lock = Lock()


def read_action_json(json_file_path: str) -> Dict:
    """
    read the action json
    :param json_file_path json file's path to read
    """
    apitestka_logger.info("json_file.py read_action_json")
    try:
        lock.acquire()
        file_path = Path(json_file_path)
        if file_path.exists() and file_path.is_file():
            with open(json_file_path) as read_file:
                return json.load(read_file)
    except APITesterJsonException:
        raise APITesterJsonException(cant_find_json_error)
    finally:
        lock.release()


def write_action_json(json_save_path: str, action_json: list) -> None:
    """
    write action json
    :param json_save_path  json save path
    :param action_json the json str include action to write
    """
    apitestka_logger.info("json_file.py write_action_json")
    try:
        lock.acquire()
        with open(json_save_path, "w+") as file_to_write:
            file_to_write.write(json.dumps(action_json, indent=4))
    except APITesterJsonException:
        raise APITesterJsonException(cant_save_json_error)
    finally:
        lock.release()
