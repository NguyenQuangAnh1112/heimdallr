from omegaconf import DictConfig

from src.components.data_ingestion import DataIntestion
from src.config.configuration import ConfigurationManager

STAGE_NAME = "Data Ingestion Stage"


class DataIngestionPipeline:
    def __init__(self, cfg: DictConfig) -> None:
        self.cfg = cfg

    def initiate_data_ingestion(self):
        config = ConfigurationManager(self.cfg)
        data_ingestion_cfg = config.get_data_ingestion_config()
        data_ingestion = DataIntestion(data_ingestion_cfg)
        data_ingestion.download_data()
