import argparse
import logging
import subprocess
import typing as t
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CMDOutput:
    output: str
    status: t.Literal["success", "fail"] = "success"


def execute(command: list[str], path: str | Path | None = None):
    logging.debug("[CMD]: Running %s.", command)
    result = subprocess.run(command, cwd=path, shell=False, text=True, capture_output=True)

    if result.returncode == 0:
        return CMDOutput(output=result.stdout.strip())
    else:
        logging.warning("[CMD]: Failed running %s:\n%s", command, result.stderr.strip())
        return CMDOutput(output=result.stderr.strip(), status="fail")


def str_to_bool(value: str) -> bool:
    """Convert string values to boolean"""
    if value.lower() in ("true", "1", "yes"):
        return True
    elif value.lower() in ("false", "0", "no"):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")
