import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# ── Tạo thư mục logs ──────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%H:%M:%S"


class ColoredFormatter(logging.Formatter):
    """Tô màu log theo level — hoạt động trên mọi terminal hỗ trợ ANSI."""

    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: GREY + LOG_FORMAT + RESET,
        logging.INFO: GREEN + LOG_FORMAT + RESET,
        logging.WARNING: YELLOW + LOG_FORMAT + RESET,
        logging.ERROR: RED + LOG_FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + LOG_FORMAT + RESET,
    }

    def format(self, record):
        formatter = logging.Formatter(self.FORMATS[record.levelno], DATE_FORMAT)
        return formatter.format(record)


def get_logger(
    name: str = "APP",
    log_file: str = "logs/app.log",
    file_level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    """
    Tạo (hoặc lấy lại) một logger theo tên.
    Singleton-safe: gọi nhiều lần với cùng name → trả về cùng 1 instance.

    Args:
        name          : Tên logger, nên đặt theo project (vd: "MYAPP")
        log_file      : Đường dẫn file log
        file_level    : Level ghi vào file  (mặc định DEBUG — ghi tất cả)
        console_level : Level in ra terminal (mặc định INFO  — bỏ qua DEBUG)
        max_bytes     : Kích thước tối đa 1 file log (mặc định 5 MB)
        backup_count  : Số file backup giữ lại (mặc định 3)

    Returns:
        logging.Logger

    Usage:
        # --- Cách 1: dùng logger mặc định (tên APP, file logs/app.log)
        from src.utils.logger import logger
        logger.info("Xin chào!")

        # --- Cách 2: tạo logger riêng cho module/service
        from src.utils.logger import get_logger
        logger = get_logger("AUTH", log_file="logs/auth.log")
        logger.warning("Token hết hạn")
    """
    logger = logging.getLogger(name)

    # Singleton: nếu đã có handler rồi thì trả về luôn
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # 1. File handler — lưu tất cả, rotate tự động
    os.makedirs(
        os.path.dirname(log_file) if os.path.dirname(log_file) else ".", exist_ok=True
    )
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
    file_handler.setLevel(file_level)

    # 2. Console handler — in màu, chỉ từ INFO trở lên
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    console_handler.setLevel(console_level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# ── Logger mặc định — import thẳng là dùng được ──────────────────────────────
logger = get_logger()
