import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from omegaconf import OmegaConf

from src.data import data_ingestion


def _base_cfg(download_dir: str, source_name: str = "roboflow"):
    return OmegaConf.create(
        {
            "data": {
                "source": {
                    "name": source_name,
                    "roboflow": {
                        "api_key_env": "ROBOFLOW_API_KEY",
                        "workspace": "test-workspace",
                        "project": "test-project",
                        "version": 3,
                        "format": "yolov8",
                    },
                },
                "paths": {"download_dir": download_dir},
            }
        }
    )


class TestDownloadRoboflow(unittest.TestCase):
    def test_missing_api_key_raises(self) -> None:
        cfg = _base_cfg(download_dir="/tmp/roboflow")

        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as ctx:
                data_ingestion._download_roboflow(cfg)

        self.assertIn("Missing Roboflow API key", str(ctx.exception))

    def test_download_invokes_roboflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = _base_cfg(download_dir=tmpdir)

            mock_rf = mock.MagicMock()
            mock_project = mock.MagicMock()
            mock_version = mock.MagicMock()
            mock_rf.workspace.return_value.project.return_value = mock_project
            mock_project.version.return_value = mock_version

            with (
                mock.patch.dict(os.environ, {"ROBOFLOW_API_KEY": "token"}, clear=True),
                mock.patch.object(data_ingestion, "Roboflow", return_value=mock_rf),
            ):
                data_ingestion._download_roboflow(cfg)

            mock_rf.workspace.assert_called_once_with("test-workspace")
            mock_rf.workspace.return_value.project.assert_called_once_with(
                "test-project"
            )
            mock_project.version.assert_called_once_with(3)
            mock_version.download.assert_called_once_with(
                "yolov8", location=str(Path(tmpdir))
            )


class TestMain(unittest.TestCase):
    def test_main_rejects_unknown_source(self) -> None:
        cfg = _base_cfg(download_dir="/tmp/roboflow", source_name="unknown")

        with mock.patch.object(data_ingestion, "log_exception") as log_exc:
            with self.assertRaises(ValueError):
                data_ingestion.main.__wrapped__(cfg)

        log_exc.assert_called_once()

    def test_main_calls_download(self) -> None:
        cfg = _base_cfg(download_dir="/tmp/roboflow")

        with mock.patch.object(data_ingestion, "_download_roboflow") as download:
            data_ingestion.main.__wrapped__(cfg)

        download.assert_called_once_with(cfg)


if __name__ == "__main__":
    unittest.main()
