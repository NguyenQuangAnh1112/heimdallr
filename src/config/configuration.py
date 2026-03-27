from pathlib import Path

from dotenv import load_dotenv
from hydra.utils import to_absolute_path
from omegaconf import DictConfig

from src.entity.config_entity import (
    DataIngestionConfig,
    DataTransformationConfig,
    DataValidationConfig,
    ModelTrainerConfig,
)


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

    def get_data_validation_config(self) -> DataValidationConfig:
        validation_cfg = self.cfg.data.validation
        data_path = str(to_absolute_path(str(validation_cfg.data_path)))
        return DataValidationConfig(
            data_path=data_path,
            data_file=str(validation_cfg.data_file),
            train=str(validation_cfg.train),
            val=str(validation_cfg.val),
            test=str(validation_cfg.test or ""),
            names=list(validation_cfg.names),
            report_dir=str(to_absolute_path(str(validation_cfg.report_dir))),
            report_file=str(validation_cfg.report_file),
            allow_empty_labels=bool(validation_cfg.get("allow_empty_labels", True)),
        )

    def get_data_transformation_config(self) -> DataTransformationConfig:
        transformation_cfg = self.cfg.data.transformation
        src_data_path = str(to_absolute_path(str(transformation_cfg.src_data_path)))
        dst_data_path = str(to_absolute_path(str(transformation_cfg.dst_data_path)))
        return DataTransformationConfig(
            src_data_path=src_data_path,
            dst_data_path=dst_data_path,
            train_dir=str(transformation_cfg.train_dir),
            val_dir=str(transformation_cfg.val_dir),
            test_dir=str(transformation_cfg.get("test_dir", "")),
            image_subdir=str(transformation_cfg.image_subdir),
            label_subdir=str(transformation_cfg.label_subdir),
        )

    def get_model_trainer_config(self) -> ModelTrainerConfig:
        trainer_cfg = self.cfg.model.trainer
        return ModelTrainerConfig(
            data_yaml_path=str(to_absolute_path(str(trainer_cfg.data_yaml_path))),
            model_name=str(trainer_cfg.model_name),
            model_store_dir=str(to_absolute_path(str(trainer_cfg.model_store_dir))),
            epochs=int(trainer_cfg.epochs),
            imgsz=int(trainer_cfg.imgsz),
            batch=int(trainer_cfg.batch),
            device=str(trainer_cfg.device),
            amp=bool(trainer_cfg.get("amp", False)),
            project_dir=str(to_absolute_path(str(trainer_cfg.project_dir))),
            run_name=str(trainer_cfg.run_name),
        )
