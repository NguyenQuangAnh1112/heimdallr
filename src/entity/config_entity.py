from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataIngestion:
    api_key: str
    workspace: str
    project: str
    version: str
    format: str
    artifacts_dir: Path
