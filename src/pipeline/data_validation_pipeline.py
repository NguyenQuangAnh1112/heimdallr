from omegaconf import DictConfig

from src.components.data_validation import DataValidation
from src.config.configuration import ConfigurationManager


class DataValidationPipeline:
    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg

    def initiate_data_validation(self):
        config = ConfigurationManager(self.cfg)
        data_validation_cfg = config.get_data_validation_config()
        data_validation = DataValidation(data_validation_cfg)
        data_validation.run()
