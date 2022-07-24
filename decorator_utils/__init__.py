import re
from pathlib import Path


def get_version(directory: Path) -> str:
    try:
        changelog = (directory / "CHANGELOG.md").read_text()
        version, *_ = re.findall(r"\[([\d.]+)]", changelog)
    except (ValueError, FileNotFoundError):
        version = "0.1.0"

    return version


__version__ = get_version(Path(__file__).parent.parent)
