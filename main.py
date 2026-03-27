import hydra
from omegaconf import DictConfig

from src.pipeline.data_ingestion_pipeline import DataIngestionPipeline
from src.pipeline.data_transformation_pipeline import DataTransformationPipeline
from src.pipeline.data_validation_pipeline import DataValidationPipeline
from src.pipeline.model_trainer_pipeline import ModelTrainerPipeline


@hydra.main(config_path="configs", config_name="config", version_base="1.3")
def main(cfg: DictConfig) -> None:
    STATE = "DATA INGESTION"
    # data_ingestion_pipeline = DataIngestionPipeline(cfg)
    # data_ingestion_pipeline.initiate_data_ingestion()
    print(f"STATE {STATE} completed")

    STATE = "DATA VALIDATION"
    # data_validation_pipeline = DataValidationPipeline(cfg)
    # data_validation_pipeline.initiate_data_validation()
    print(f"STATE {STATE} completed")

    STATE = "DATA TRANSFORMATION"
    # data_transformation_pipeline = DataTransformationPipeline(cfg)
    # data_transformation_pipeline.initiate_data_transformation()
    print(f"STATE {STATE} completed")

    STATE = "MODEL TRAINER"
    model_trainer_pipeline = ModelTrainerPipeline(cfg)
    model_trainer_pipeline.initiate_model_trainer()
    print(f"STATE {STATE} completed")


if __name__ == "__main__":
    main()
