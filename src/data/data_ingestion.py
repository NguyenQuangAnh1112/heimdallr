from __future__ import annotations

import os
from pathlib import Path

import hydra
from omegaconf import DictConfig
from roboflow import Roboflow

from src.utils.exception import log_exception
from src.utils.logger import logger


# Downloads a Roboflow dataset into the configured download directory.
def _download_roboflow(cfg: DictConfig) -> None:
    source = cfg.data.source
    api_key = os.getenv(source.roboflow.api_key_env)
    if not api_key:
        raise ValueError(
            f"Missing Roboflow API key. Set env var {source.roboflow.api_key_env}."
        )

    download_dir = Path(cfg.data.paths.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Downloading Roboflow dataset workspace=%s project=%s version=%s format=%s",
        source.roboflow.workspace,
        source.roboflow.project,
        source.roboflow.version,
        source.roboflow.format,
    )

    rf = Roboflow(api_key=api_key)
    project = rf.workspace(source.roboflow.workspace).project(source.roboflow.project)
    project.version(source.roboflow.version).download(
        source.roboflow.format, location=str(download_dir)
    )
    logger.info("Download completed. Output dir: %s", download_dir)


@hydra.main(config_path="configs", config_name="config", version_base="1.3")
def main(cfg: DictConfig) -> None:
    try:
        if cfg.data.source.name != "roboflow":
            raise ValueError(f"Unsupported data source: {cfg.data.source.name}")
        _download_roboflow(cfg)
    except Exception as exc:
        log_exception(exc, logger=logger)
        raise


if __name__ == "__main__":
    main()  # type: ignore[call-arg]
