from .constant import get_browser_lib as get_browser_lib, logger as logger
from pathlib import Path

def combine(input_folder: Path, output_folder: Path, config: Path | None, name: str | None = None, reports: str = 'v8') -> None: ...
