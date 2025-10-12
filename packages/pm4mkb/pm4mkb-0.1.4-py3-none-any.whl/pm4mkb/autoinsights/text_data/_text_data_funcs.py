from __future__ import annotations
from pathlib import Path


DIR_PATH = Path(__file__).absolute().parent


def get_mistake_lemmas_path() -> Path:
    return DIR_PATH / "mistakes.txt"


def get_reversal_lemmas_path() -> Path:
    return DIR_PATH / "reversal.txt"
