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


@dataclass
class DataTransformationConfig:
    src_data_path: str
    dst_data_path: str
    train_dir: str
    val_dir: str
    test_dir: str
    image_subdir: str
    label_subdir: str
