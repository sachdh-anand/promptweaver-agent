import logging
import os
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

try:
    import colorama
    colorama.init(autoreset=True)
    Fore = colorama.Fore
    Style = colorama.Style
except ImportError:
    class DummyStyle:
        def __getattr__(self, name: str) -> str:
            return ""
    Fore = DummyStyle()
    Style = DummyStyle()

class LogSymbols:
    DEBUG = "🔍"
    INFO = "ℹ️ "
    SUCCESS = "✅"
    WARNING = "⚠️ "
    ERROR = "❌"
    CRITICAL = "🚨"
    START = "▶️ "
    END = "⏹️ "
    DIVIDER = "━"
    TEST = "🧪"
    API = "🌐"
    MODEL = "🤖"

LOG_LEVEL_MAP: Dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

DEFAULT_LOG_LEVEL_NAME = "INFO"
APP_LOGGER_NAME = Path(__file__).resolve().parents[2].name.split("-")[0]
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class ConsoleFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }
    LEVEL_SYMBOLS = {
        logging.DEBUG: LogSymbols.DEBUG,
        logging.INFO: LogSymbols.INFO,
        logging.WARNING: LogSymbols.WARNING,
        logging.ERROR: LogSymbols.ERROR,
        logging.CRITICAL: LogSymbols.CRITICAL,
    }
    MAX_LEVEL_LEN = max(len(logging.getLevelName(level)) for level in LEVEL_COLORS.keys())
    SIMPLE_CONSOLE_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def __init__(self, fmt='%(asctime)s │ %(levelname)s │ %(name)-15s │ %(message)s', datefmt='%H:%M:%S', style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.app_name_prefix = APP_LOGGER_NAME + "."
        self.app_name_exact = APP_LOGGER_NAME
        self._simple_formatter = logging.Formatter(fmt=self.SIMPLE_CONSOLE_FMT, datefmt=self.datefmt)

    def is_app_log(self, record):
        return record.name == self.app_name_exact or record.name.startswith(self.app_name_prefix)

    def format(self, record):
        try:
            original_msg = record.getMessage()
        except Exception:
            original_msg = str(record.msg)

        if self.is_app_log(record):
            log_color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
            level_name_str = logging.getLevelName(record.levelno)
            padding = ' ' * (self.MAX_LEVEL_LEN - len(level_name_str))
            record.levelname = f"{log_color}{level_name_str}{padding}{Style.RESET_ALL}"
            log_symbol = self.LEVEL_SYMBOLS.get(record.levelno, "")
            current_msg = f"{log_symbol} {original_msg}"
            original_args = record.args
            record.msg = current_msg
            record.args = []
            formatted = super().format(record)
            record.levelname = level_name_str
            record.msg = original_msg
            record.args = original_args
            return formatted
        return self._simple_formatter.format(record)

class FileFormatter(logging.Formatter):
    LEVEL_SYMBOLS = ConsoleFormatter.LEVEL_SYMBOLS
    MAX_LEVEL_LEN = ConsoleFormatter.MAX_LEVEL_LEN
    SIMPLE_FILE_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def __init__(self, fmt='%(asctime)s │ %(levelname)-9s │ %(name)-15s │ %(message)s', datefmt='%H:%M:%S', style='%'):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.app_name_prefix = APP_LOGGER_NAME + "."
        self.app_name_exact = APP_LOGGER_NAME
        self._simple_formatter = logging.Formatter(fmt=self.SIMPLE_FILE_FMT, datefmt=self.datefmt)

    def is_app_log(self, record):
        return record.name == self.app_name_exact or record.name.startswith(self.app_name_prefix)

    def format(self, record):
        try:
            original_msg = record.getMessage()
        except Exception:
            original_msg = str(record.msg)
        level_name_str = logging.getLevelName(record.levelno)
        padding = ' ' * (self.MAX_LEVEL_LEN - len(level_name_str))
        record.levelname = f"{level_name_str}{padding}"
        log_symbol = self.LEVEL_SYMBOLS.get(record.levelno, "")
        if self.is_app_log(record):
            current_msg = f"{log_symbol} {original_msg}"
        else:
            current_msg = f"[lib] {original_msg}"
        original_args = record.args
        record.msg = current_msg
        record.args = []
        formatted = super().format(record)
        record.levelname = level_name_str
        record.msg = original_msg
        record.args = original_args
        return ANSI_ESCAPE_PATTERN.sub('', formatted)

class StdoutInterceptor:
    def __init__(self, log_path: str):
        self.terminal = sys.stdout
        self.log = open(log_path, "a", encoding="utf-8", buffering=1)

    def write(self, message):
        self.terminal.write(message)
        cleaned = ANSI_ESCAPE_PATTERN.sub('', message)  # 🧼 strip ANSI before writing
        self.log.write(cleaned)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

class Logger:
    _is_setup = False
    _app_logger_instance: Optional[logging.Logger] = None
    ENV_VAR_LOG_LEVEL = "LOG_LEVEL"
    ENV_VAR_LOG_FILE_ENABLE = "LOG_FILE_ENABLE"
    ENV_VAR_LOG_FILE_PATH = "LOG_FILE_PATH"
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_FILE_ENABLE = True

    @staticmethod
    def get_default_log_file() -> Path:
        project_root = Path(__file__).resolve().parent.parent.parent
        log_dir = project_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / f"{APP_LOGGER_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    @staticmethod
    def setup() -> logging.Logger:
        if Logger._is_setup:
            return Logger._app_logger_instance
        log_level_name = os.getenv(Logger.ENV_VAR_LOG_LEVEL, DEFAULT_LOG_LEVEL_NAME).upper()
        log_level = LOG_LEVEL_MAP.get(log_level_name, Logger.DEFAULT_LOG_LEVEL)
        log_file_enable = os.getenv(Logger.ENV_VAR_LOG_FILE_ENABLE, str(Logger.DEFAULT_FILE_ENABLE)).lower() == "true"
        log_file_path_override = os.getenv(Logger.ENV_VAR_LOG_FILE_PATH, None)

        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        app_logger = logging.getLogger(APP_LOGGER_NAME)
        app_logger.setLevel(log_level)
        app_logger.propagate = False
        for handler in app_logger.handlers[:]:
            app_logger.removeHandler(handler)

        console_fmt = '%(asctime)s │ %(levelname)s │ %(name)-15s │ %(message)s'
        file_fmt = '%(asctime)s │ %(levelname)-9s │ %(name)-15s │ %(message)s'
        date_fmt = '%H:%M:%S'

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ConsoleFormatter(fmt=console_fmt, datefmt=date_fmt))
        app_logger.addHandler(console_handler)

        actual_log_file = None
        if log_file_enable:
            actual_log_file = Path(log_file_path_override) if log_file_path_override else Logger.get_default_log_file()
            actual_log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(str(actual_log_file), encoding='utf-8', delay=True)
            file_handler.setFormatter(FileFormatter(fmt=file_fmt, datefmt=date_fmt))
            app_logger.addHandler(file_handler)
            root_file_handler = logging.FileHandler(str(actual_log_file), encoding='utf-8', delay=True)
            root_file_handler.setFormatter(FileFormatter(fmt=file_fmt, datefmt=date_fmt))
            root_logger.addHandler(root_file_handler)
            sys.stdout = StdoutInterceptor(str(actual_log_file))
            sys.stderr = sys.stdout
            print(f"{LogSymbols.INFO} Logging to file: {actual_log_file}")

        lib_level = LOG_LEVEL_MAP.get(os.getenv("LIBRARY_LOG_LEVEL", "WARNING").upper(), logging.WARNING)
        for lib in ["httpx", "LiteLLM", "openai", "crewai", "chromadb", "docling"]:
            lib_logger = logging.getLogger(lib)
            lib_logger.setLevel(lib_level)
            lib_logger.handlers.clear()
            lib_logger.propagate = False

        divider = f"{LogSymbols.DIVIDER * 60}"
        app_logger.info(divider)
        app_logger.info(f"Logger Setup Complete (App Level: {log_level_name}) {LogSymbols.SUCCESS}")
        if actual_log_file:
            app_logger.info(f"File Logging: Enabled ({str(actual_log_file)})")
        else:
            app_logger.info("File Logging: Disabled")
        app_logger.info(f"Library Log Level: {os.getenv('LIBRARY_LOG_LEVEL', 'WARNING').upper()}")
        app_logger.info(divider)

        Logger._is_setup = True
        Logger._app_logger_instance = app_logger
        return app_logger

def get_logger(name: str) -> logging.Logger:
    if not Logger._is_setup:
        Logger.setup()
    if name == "__main__":
        return logging.getLogger(f"{APP_LOGGER_NAME}.main")
    if name.startswith(APP_LOGGER_NAME + "."):
        return logging.getLogger(name)
    if name == APP_LOGGER_NAME:
        return logging.getLogger(APP_LOGGER_NAME)
    return logging.getLogger(f"{APP_LOGGER_NAME}.{name.split('.')[-1]}")