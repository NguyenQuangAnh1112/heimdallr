from pathlib import Path
import shutil

from ultralytics import YOLO

from src.entity.config_entity import ModelTrainerConfig
from src.utils.logger import logger


class ModelTrainer:
    def __init__(self, cfg: ModelTrainerConfig) -> None:
        self.cfg = cfg

    def _resolve_model_source(self) -> str:
        model_input = Path(self.cfg.model_name)
        if model_input.exists():
            logger.info("Use local model from config: %s", model_input)
            return str(model_input)

        model_store_dir = Path(self.cfg.model_store_dir)
        model_store_dir.mkdir(parents=True, exist_ok=True)

        cached_model_path = model_store_dir / self.cfg.model_name
        if cached_model_path.exists():
            logger.info("Use cached model: %s", cached_model_path)
            return str(cached_model_path)

        logger.info(
            "Model cache not found. Downloading model '%s'.", self.cfg.model_name
        )
        downloaded_model = YOLO(self.cfg.model_name)

        ckpt_path_value = getattr(downloaded_model, "ckpt_path", None)
        if ckpt_path_value:
            ckpt_path = Path(ckpt_path_value)
            if ckpt_path.exists():
                shutil.copy2(ckpt_path, cached_model_path)
                logger.info("Cached downloaded model to: %s", cached_model_path)
                return str(cached_model_path)

        logger.warning(
            "Could not determine downloaded checkpoint path. Continue with model '%s'.",
            self.cfg.model_name,
        )
        return self.cfg.model_name

    def train(self) -> Path:
        data_yaml = Path(self.cfg.data_yaml_path)
        if not data_yaml.exists():
            raise FileNotFoundError(f"Dataset yaml not found: {data_yaml}")

        project_dir = Path(self.cfg.project_dir)
        project_dir.mkdir(parents=True, exist_ok=True)

        model_source = self._resolve_model_source()
        logger.info("Start training with model '%s'", model_source)
        model = YOLO(model_source)

        results = model.train(
            data=str(data_yaml),
            epochs=self.cfg.epochs,
            imgsz=self.cfg.imgsz,
            batch=self.cfg.batch,
            device=self.cfg.device,
            amp=self.cfg.amp,
            project=str(project_dir),
            name=self.cfg.run_name,
        )

        save_dir = Path(results.save_dir)
        logger.info("Training completed. Artifacts saved at: %s", save_dir)
        return save_dir
