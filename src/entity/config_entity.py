from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataIngestionConfig:
    api_key: str
    workspace: str
    project: str
    version: int
    format: str
    artifacts_dir: Path
