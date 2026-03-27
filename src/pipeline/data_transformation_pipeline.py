from omegaconf import DictConfig

from src.components.data_transformation import DataTransformation
from src.config.configuration import ConfigurationManager


class DataTransformationPipeline:
    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg

    def initiate_data_transformation(self) -> None:
        config = ConfigurationManager(self.cfg)
        data_transformation_cfg = config.get_data_transformation_config()
        data_transformation = DataTransformation(data_transformation_cfg)
        data_transformation.run()
