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
    dataset_dir: Path
    train_dir: Path
    val_dir: Path
    test_dir: Path
    num_classes: int
    class_names: List[str]
    image_size: int
    min_bbox_area: float
    max_bbox_area: float
    check_duplicates: bool
    check_empty_labels: bool
