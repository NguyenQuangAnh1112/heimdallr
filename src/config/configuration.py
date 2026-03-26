from pathlib import Path

from dotenv import load_dotenv
from hydra.utils import to_absolute_path
from omegaconf import DictConfig

from src.entity.config_entity import DataIngestionConfig


class ConfigurationManager:
    def __init__(self, cfg: DictConfig, env_file: str = ".env"):
        self.cfg = cfg
        self._load_env_file(env_file)

    @staticmethod
    def _load_env_file(env_file: str) -> None:
        env_path = Path(to_absolute_path(env_file))
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        ingestion_cfg = self.cfg.data.ingestion
        artifacts_dir = Path(to_absolute_path(str(ingestion_cfg.artifacts_dir)))
        api_key = str(ingestion_cfg.api_key or "")
        if not api_key:
            raise ValueError(
                "Missing ROBOFLOW_API_KEY. Please set environment variable first."
            )
        return DataIngestionConfig(
            api_key=api_key,
            workspace=str(ingestion_cfg.workspace),
            project=str(ingestion_cfg.project),
            version=int(ingestion_cfg.version),
            format=str(ingestion_cfg.format),
            artifacts_dir=artifacts_dir,
        )
