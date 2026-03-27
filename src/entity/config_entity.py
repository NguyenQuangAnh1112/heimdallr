from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class DataIngestionConfig:
    api_key: str
    workspace: str
    project: str
    version: int
    format: str
    artifacts_dir: Path


@dataclass
class DataValidationConfig:
    data_path: str
    data_file: str
    train: str
    val: str
    test: str
    names: List[str]
    report_dir: str
    report_file: str
    allow_empty_labels: bool
