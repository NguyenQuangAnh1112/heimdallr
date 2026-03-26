from pathlib import Path

from hydra.utils import to_absolute_path
from omegaconf import DictConfig

from src.entity.config_entity import DataIngestion


class ConfigurationManager:
    def __init__(self, cfg: DictConfig):
        self.cfg = cfg

    def get_data_ingestion_config(self) -> DataIngestion:
        ingestion_cfg = self.cfg.data.ingestion_
        artifacts_dir = Path(to_absolute_path(str(ingestion_cfg.artifacts_dir)))
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        api_key = str(ingestion_cfg.api_key or "")
        if not api_key:
            raise ValueError(
                "Missing ROBOFLOW_API_KEY. Please set environment variable first."
            )
        return DataIngestion(
            api_key=api_key,
            workspace=str(ingestion_cfg.workspace),
            project=str(ingestion_cfg.project),
            version=str(ingestion_cfg.version),
            format=str(ingestion_cfg.format),
            artifacts_dir=artifacts_dir,
        )
