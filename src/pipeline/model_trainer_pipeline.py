from omegaconf import DictConfig

from src.components.model_trainer import ModelTrainer
from src.config.configuration import ConfigurationManager


class ModelTrainerPipeline:
    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg

    def initiate_model_trainer(self) -> None:
        config = ConfigurationManager(self.cfg)
        model_trainer_cfg = config.get_model_trainer_config()
        model_trainer = ModelTrainer(model_trainer_cfg)
        model_trainer.train()
