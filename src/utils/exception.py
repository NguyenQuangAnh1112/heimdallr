import functools
import sys
import threading
import traceback
from datetime import datetime
from typing import Any, Callable, Optional

from src.utils.logger import logger as default_logger

# ══════════════════════════════════════════════════════════════════════════════
# 1. CUSTOM EXCEPTIONS — kế thừa theo tầng, dùng cho mọi loại project
# ══════════════════════════════════════════════════════════════════════════════


class AppError(Exception):
    """
    Lỗi gốc của toàn bộ ứng dụng.
    Mọi custom exception đều nên kế thừa từ đây để dễ catch tổng.

    Usage:
        try:
            ...
        except AppError:
            # Bắt tất cả lỗi của app
    """

    pass


# ── Web / API ─────────────────────────────────────────────────────────────────
class ValidationError(AppError):
    """Dữ liệu đầu vào không hợp lệ (form, request body, params...)"""

    pass


class NotFoundError(AppError):
    """Resource không tồn tại"""

    pass


class PermissionError(AppError):
    """Không có quyền thực hiện hành động"""

    pass


# ── Data / ML pipeline ────────────────────────────────────────────────────────
class DataProcessingError(AppError):
    """Lỗi trong quá trình xử lý / transform dữ liệu"""

    pass


class ModelError(AppError):
    """Lỗi liên quan đến model (load, predict, train...)"""

    pass


# ── External services ─────────────────────────────────────────────────────────
class ExternalServiceError(AppError):
    """Lỗi khi gọi API bên ngoài, DB, queue..."""

    pass


class TimeoutError(AppError):
    """Request / task chạy quá lâu"""

    pass


# ══════════════════════════════════════════════════════════════════════════════
# 2. FORMATTER — in traceback + local variables đầy đủ
# ══════════════════════════════════════════════════════════════════════════════


def format_exception_detail(error: Exception) -> str:
    """
    Trả về chuỗi mô tả lỗi đầy đủ:
      - Loại lỗi, message
      - Full traceback chain
      - Local variables tại điểm crash (truncated nếu quá dài)
    """
    exc_type, exc_value, exc_tb = sys.exc_info()

    # Full traceback
    tb_chain = (
        "".join(traceback.format_tb(exc_tb)).strip() if exc_tb else "(no traceback)"
    )

    # Đi đến frame trong cùng
    innermost = exc_tb
    if innermost:
        while innermost.tb_next:
            innermost = innermost.tb_next
        file_name = innermost.tb_frame.f_code.co_filename
        func_name = innermost.tb_frame.f_code.co_name
        line_number = innermost.tb_lineno
        local_vars = {
            k: (repr(v)[:300] + "...") if len(repr(v)) > 300 else repr(v)
            for k, v in innermost.tb_frame.f_locals.items()
        }
    else:
        file_name = func_name = "(unknown)"
        line_number = 0
        local_vars = {}

    # Fix: tách unpack ra biến riêng để tránh lỗi syntax với * inline
    local_var_lines = (
        [f"    {k} = {v}" for k, v in local_vars.items()]
        if local_vars
        else ["    (none)"]
    )

    sep = "=" * 70
    dash = "-" * 70
    lines = [
        f"\n{sep}",
        f"  EXCEPTION — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        sep,
        f"  File     : {file_name}",
        f"  Function : {func_name}()",
        f"  Line     : {line_number}",
        f"  Error    : {type(error).__name__}: {error}",
        dash,
        "  TRACEBACK (most recent call last):",
        tb_chain,
        dash,
        "  LOCAL VARIABLES at crash site:",
        *local_var_lines,
        sep,
    ]
    return "\n".join(lines)


def log_exception(error: Exception, logger=default_logger) -> None:
    detail = format_exception_detail(error)
    logger.critical(detail)


def install_exception_hook(logger=default_logger) -> None:
    def _hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            return sys.__excepthook__(exc_type, exc_value, exc_tb)
        error = (
            exc_value if isinstance(exc_value, Exception) else Exception(str(exc_value))
        )
        log_exception(error, logger=logger)

    sys.excepthook = _hook

    threading_excepthook = getattr(threading, "excepthook", None)
    if callable(threading_excepthook):

        def _threading_hook(args):
            if isinstance(args.exc_value, KeyboardInterrupt):
                return
            error = (
                args.exc_value
                if isinstance(args.exc_value, Exception)
                else Exception(str(args.exc_value))
            )
            log_exception(error, logger=logger)

        threading.excepthook = _threading_hook


# ══════════════════════════════════════════════════════════════════════════════
# 3. DECORATOR FACTORY — dùng cho mọi loại project
# ══════════════════════════════════════════════════════════════════════════════


def handle_errors(
    *catch: type,
    return_on_error: Optional[Any] = None,
    reraise: bool = False,
    logger=default_logger,
):
    """
    Decorator factory bắt lỗi linh hoạt — dùng cho mọi loại project.

    Args:
        *catch         : Các exception type muốn bắt riêng (tùy chọn).
                         Nếu không truyền → bắt tất cả Exception.
        return_on_error: Giá trị trả về khi có lỗi.
                         None  → re-raise lỗi (mặc định khi reraise=True)
        reraise        : True  → log xong rồi throw lại lỗi gốc.
                         False → nuốt lỗi, trả về return_on_error.
        logger         : Logger dùng để ghi (mặc định logger của app).

    Usage:
        # --- Bắt tất cả lỗi, trả về None khi lỗi
        @handle_errors(return_on_error=None)
        def get_user(user_id): ...

        # --- Bắt riêng ValidationError, re-raise lỗi khác
        @handle_errors(ValidationError, reraise=True)
        def create_order(data): ...

        # --- Shortcut he (xem cuối file)
        @he
        def train_model(X, y): ...
    """
    # Dùng tuple[type, ...] để isinstance() nhận — không dùng trực tiếp trong except
    catch_types = tuple(catch) if catch else (Exception,)

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Nếu có chỉ định loại lỗi cụ thể mà không khớp → throw lại
                if not isinstance(e, catch_types):
                    raise

                detail = format_exception_detail(e)
                logger.critical(detail)

                if reraise:
                    raise

                return return_on_error

        return wrapper

    return decorator


# ══════════════════════════════════════════════════════════════════════════════
# 4. SHORTCUTS — import nhanh, dùng liền
# ══════════════════════════════════════════════════════════════════════════════

# Dùng chung — bắt mọi lỗi, trả về None
he = handle_errors()

# Dùng khi muốn lỗi nổi lên sau khi đã log (vd: FastAPI, Django)
he_raise = handle_errors(reraise=True)
