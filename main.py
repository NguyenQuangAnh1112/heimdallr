import hydra
from omegaconf import DictConfig

from src.config.configuration import ConfigurationManager
from src.pipeline.data_ingestion_pipeline import DataIngestionPipeline


@hydra.main(config_path="configs", config_name="config", version_base="1.3")
def main(cfg: DictConfig) -> None:
    data_ingestion_pipeline = DataIngestionPipeline(cfg)
    data_ingestion_pipeline.initiate_data_ingestion()


if __name__ == "__main__":
    main()
