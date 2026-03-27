import hydra
from omegaconf import DictConfig

from src.pipeline.data_ingestion_pipeline import DataIngestionPipeline
from src.pipeline.data_validation_pipeline import DataValidationPipeline


@hydra.main(config_path="configs", config_name="config", version_base="1.3")
def main(cfg: DictConfig) -> None:
    STATE = "DATA INGESTION"
    # data_ingestion_pipeline = DataIngestionPipeline(cfg)
    # data_ingestion_pipeline.initiate_data_ingestion()
    print(f"STATE {STATE} completed")

    STATE = "DATA VALIDATION"
    data_validation_pipeline = DataValidationPipeline(cfg)
    data_validation_pipeline.initiate_data_validation()
    print(f"STATE {STATE} completed")


if __name__ == "__main__":
    main()
