from pathlib import Path

from roboflow import Roboflow

from src.entity.config_entity import DataIngestionConfig


class DataIntestion:
    def __init__(self, config: DataIngestionConfig):
        self.cfg = config

    def download_data(self):
        artifacts_dir = Path(self.cfg.artifacts_dir).resolve()
        rf = Roboflow(api_key=self.cfg.api_key)
        proj = rf.workspace(self.cfg.workspace).project(self.cfg.project)
        dataset = proj.version(self.cfg.version).download(
            self.cfg.format, location=str(artifacts_dir), overwrite=True
        )
        return dataset.location
