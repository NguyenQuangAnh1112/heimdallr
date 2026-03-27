from pathlib import Path
from PIL import Image
import shutil

from src.entity.config_entity import DataTransformationConfig
from src.utils.logger import logger


class DataTransformation:
    def __init__(self, cfg: DataTransformationConfig) -> None:
        self.cfg = cfg

    def transform_dataset(
        self,
        src_img_dir: Path,
        src_lbl_dir: Path,
        dst_img_dir: Path,
        dst_lbl_dir: Path,
    ) -> tuple[int, int]:
        kept, removed = 0, 0

        for img_path in src_img_dir.glob("*.*"):
            label_path = src_lbl_dir / f"{img_path.stem}.txt"

            if not label_path.exists():
                continue

            try:
                with Image.open(img_path) as img:
                    img.verify()

                with Image.open(img_path) as img:
                    rgb_img = img.convert("RGB")

                dst_img_path = dst_img_dir / img_path.name
                dst_lbl_path = dst_lbl_dir / label_path.name

                dst_img_path.parent.mkdir(parents=True, exist_ok=True)
                dst_lbl_path.parent.mkdir(parents=True, exist_ok=True)

                rgb_img.save(dst_img_path)
                shutil.copy(label_path, dst_lbl_path)
                kept += 1
            except Exception:
                removed += 1

        return kept, removed

    def run(self) -> None:
        splits = {
            "train": self.cfg.train_dir,
            "val": self.cfg.val_dir,
            "test": self.cfg.test_dir,
        }

        total_kept, total_removed = 0, 0

        src_root = Path(self.cfg.src_data_path)
        dst_root = Path(self.cfg.dst_data_path)

        for split_name, split_dir in splits.items():
            if not split_dir:
                logger.info("Skip optional split '%s' (not configured).", split_name)
                continue

            src_img_dir = src_root / split_dir / self.cfg.image_subdir
            src_lbl_dir = src_root / split_dir / self.cfg.label_subdir
            dst_img_dir = dst_root / split_dir / self.cfg.image_subdir
            dst_lbl_dir = dst_root / split_dir / self.cfg.label_subdir

            if not src_img_dir.exists() or not src_lbl_dir.exists():
                logger.warning(
                    "Skip split '%s' because source path is missing (images=%s, labels=%s)",
                    split_name,
                    src_img_dir,
                    src_lbl_dir,
                )
                continue

            kept, removed = self.transform_dataset(
                src_img_dir=src_img_dir,
                src_lbl_dir=src_lbl_dir,
                dst_img_dir=dst_img_dir,
                dst_lbl_dir=dst_lbl_dir,
            )

            total_kept += kept
            total_removed += removed

            logger.info("Split '%s' - kept: %s, removed: %s", split_name, kept, removed)

        logger.info(
            "Data transformation completed. Total kept: %s, total removed: %s",
            total_kept,
            total_removed,
        )
