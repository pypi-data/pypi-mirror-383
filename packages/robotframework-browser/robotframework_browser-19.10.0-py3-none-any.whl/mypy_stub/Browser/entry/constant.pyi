import logging
from _typeshed import Incomplete
from pathlib import Path

INSTALLATION_DIR: Incomplete
NODE_MODULES: Incomplete
IS_WINDOWS: Incomplete
SHELL: Incomplete
ROOT_FOLDER: Incomplete
LOG_FILE: str
INSTALL_LOG: Incomplete
PLAYWRIGHT_BROWSERS_PATH: str
IS_TERMINAL: Incomplete
logger: Incomplete
handlers: list[logging.StreamHandler]

def log(message: str, silent_mode: bool = False): ...
def write_marker(silent_mode: bool = False): ...
def get_browser_lib(): ...
def get_playwright_browser_path() -> Path: ...
def ensure_playwright_browsers_path() -> None: ...
