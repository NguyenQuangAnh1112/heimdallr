from datetime import datetime
from pathlib import Path

from ultralytics.data.utils import check_det_dataset

from src.entity.config_entity import DataValidationConfig
from src.utils.logger import logger


class DataValidation:
    def __init__(self, cfg: DataValidationConfig):
        self.cfg = cfg

    def check_dataset_with_ultralytics(self) -> DataValidationConfig:
        yaml_path = Path(self.cfg.data_path) / self.cfg.data_file
        data = check_det_dataset(str(yaml_path))

        names_raw = data.get("names", [])
        class_names = (
            list(names_raw.values()) if isinstance(names_raw, dict) else list(names_raw)
        )

        dataset_root = Path(data["path"])

        def resolve_dataset_path(value: str | None) -> str:
            if not value:
                return ""
            candidate = Path(value)
            if candidate.is_absolute():
                return str(candidate)
            return str(dataset_root / candidate)

        normalized_cfg = DataValidationConfig(
            data_path=str(dataset_root),
            data_file=self.cfg.data_file,
            train=resolve_dataset_path(data.get("train")),
            val=resolve_dataset_path(data.get("val")),
            test=resolve_dataset_path(data.get("test")),
            names=class_names,
            report_dir=self.cfg.report_dir,
            report_file=self.cfg.report_file,
            allow_empty_labels=self.cfg.allow_empty_labels,
        )

        self.cfg = normalized_cfg
        return normalized_cfg

    @staticmethod
    def _is_image_file(path: Path) -> bool:
        return path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    @staticmethod
    def _label_dir_from_image_dir(image_dir: Path) -> Path:
        if image_dir.name == "images":
            return image_dir.parent / "labels"
        return image_dir.parent / "labels" / image_dir.name

    def _validate_label_file(
        self, label_file: Path, num_classes: int
    ) -> tuple[list[str], list[str]]:
        issues: list[str] = []
        warnings: list[str] = []
        lines = label_file.read_text(encoding="utf-8").splitlines()

        if not lines:
            if self.cfg.allow_empty_labels:
                warnings.append(f"{label_file}: empty label file (allowed)")
            else:
                issues.append(f"{label_file}: empty label file")
            return issues, warnings

        seen = set()
        for idx, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
            if not line:
                issues.append(f"{label_file}:{idx}: empty line")
                continue
            if line in seen:
                issues.append(f"{label_file}:{idx}: duplicate bbox row")
            seen.add(line)

            parts = line.split()
            if len(parts) != 5:
                issues.append(
                    f"{label_file}:{idx}: expected 5 fields, got {len(parts)}"
                )
                continue

            try:
                cls_id = int(parts[0])
                x_center, y_center, width, height = map(float, parts[1:])
            except ValueError:
                issues.append(f"{label_file}:{idx}: non-numeric values")
                continue

            if cls_id < 0 or cls_id >= num_classes:
                issues.append(
                    f"{label_file}:{idx}: class id {cls_id} out of range [0, {num_classes - 1}]"
                )

            for value, name in (
                (x_center, "x_center"),
                (y_center, "y_center"),
                (width, "width"),
                (height, "height"),
            ):
                if value < 0.0 or value > 1.0:
                    issues.append(
                        f"{label_file}:{idx}: {name} must be in [0,1], got {value}"
                    )
            if width <= 0 or height <= 0:
                issues.append(f"{label_file}:{idx}: width/height must be > 0")

        return issues, warnings

    def _validate_split(
        self, split_name: str, image_dir_value: str, num_classes: int
    ) -> tuple[list[str], list[str]]:
        issues: list[str] = []
        warnings: list[str] = []
        if not image_dir_value:
            if split_name == "test":
                logger.info("Skip optional '%s' split (not configured).", split_name)
                return issues, warnings
            issues.append(f"{split_name}: path is missing")
            return issues, warnings

        image_dir = Path(image_dir_value)
        if not image_dir.exists() or not image_dir.is_dir():
            issues.append(f"{split_name}: image dir not found -> {image_dir}")
            return issues, warnings

        label_dir = self._label_dir_from_image_dir(image_dir)
        if not label_dir.exists() or not label_dir.is_dir():
            issues.append(f"{split_name}: label dir not found -> {label_dir}")
            return issues, warnings

        images = [
            p for p in image_dir.iterdir() if p.is_file() and self._is_image_file(p)
        ]
        labels = [
            p for p in label_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
        ]

        if not images:
            issues.append(f"{split_name}: no image files found in {image_dir}")
            return issues, warnings

        image_stems = {p.stem for p in images}
        label_stems = {p.stem for p in labels}

        missing_labels = image_stems - label_stems
        orphan_labels = label_stems - image_stems
        if missing_labels:
            issues.append(
                f"{split_name}: {len(missing_labels)} images without labels (example: {next(iter(missing_labels))})"
            )
        if orphan_labels:
            issues.append(
                f"{split_name}: {len(orphan_labels)} labels without images (example: {next(iter(orphan_labels))})"
            )

        for label_file in labels:
            file_issues, file_warnings = self._validate_label_file(
                label_file, num_classes=num_classes
            )
            issues.extend(file_issues)
            warnings.extend(file_warnings)

        logger.info(
            "Validated split '%s': %s images, %s labels",
            split_name,
            len(images),
            len(labels),
        )
        return issues, warnings

    def run(self) -> DataValidationConfig:
        normalized_cfg = self.check_dataset_with_ultralytics()

        num_classes = len(normalized_cfg.names)
        if num_classes == 0:
            raise ValueError("No class names found after parsing dataset yaml.")

        issues: list[str] = []
        warnings: list[str] = []

        split_issues, split_warnings = self._validate_split(
            "train", normalized_cfg.train, num_classes
        )
        issues.extend(split_issues)
        warnings.extend(split_warnings)

        split_issues, split_warnings = self._validate_split(
            "val", normalized_cfg.val, num_classes
        )
        issues.extend(split_issues)
        warnings.extend(split_warnings)

        split_issues, split_warnings = self._validate_split(
            "test", normalized_cfg.test, num_classes
        )
        issues.extend(split_issues)
        warnings.extend(split_warnings)

        report_path = self._write_report(normalized_cfg, issues, warnings)

        if issues:
            preview = "\n".join(f"- {msg}" for msg in issues[:20])
            extra = (
                "" if len(issues) <= 20 else f"\n... and {len(issues) - 20} more issues"
            )
            raise ValueError(
                f"Data validation failed with {len(issues)} issue(s). Report: {report_path}\n{preview}{extra}"
            )

        logger.info(
            "Data validation passed for dataset at %s. Report: %s",
            normalized_cfg.data_path,
            report_path,
        )
        if warnings:
            logger.warning("Data validation has %s warning(s).", len(warnings))
        return normalized_cfg

    def _write_report(
        self, cfg: DataValidationConfig, issues: list[str], warnings: list[str]
    ) -> Path:
        report_dir = Path(cfg.report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / cfg.report_file

        lines = [
            "Data Validation Report",
            "=" * 22,
            f"Timestamp: {datetime.now().isoformat(timespec='seconds')}",
            f"Dataset root: {cfg.data_path}",
            f"YAML file: {Path(cfg.data_path) / cfg.data_file}",
            f"Train: {cfg.train}",
            f"Val: {cfg.val}",
            f"Test: {cfg.test or '(not configured)'}",
            f"Classes ({len(cfg.names)}): {', '.join(cfg.names)}",
            f"Status: {'FAILED' if issues else 'PASSED'}",
            f"Total issues: {len(issues)}",
            f"Total warnings: {len(warnings)}",
            f"Allow empty labels: {cfg.allow_empty_labels}",
            "",
        ]

        if issues:
            lines.append("Issues:")
            lines.extend(f"- {issue}" for issue in issues)
            lines.append("")

        if warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in warnings)
            lines.append("")

        if not issues and not warnings:
            lines.append("No issues found.")

        report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return report_path
