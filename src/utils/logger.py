# src/utils/logger.py

import logging
import os
import sys
import io
import re  # Ensure 're' is imported at the top level
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, TextIO, Set, Dict, Any

# --- Attempt to import colorama ---
try:
    import colorama
    colorama.init(autoreset=True) # Autoreset ensures style doesn't leak
    Fore = colorama.Fore
    Style = colorama.Style
    # COLORAMA_AVAILABLE is not strictly needed if we just check isinstance(Fore, DummyStyle)
except ImportError:
    # Define dummy Fore/Style if colorama is not installed
    class DummyStyle:
        def __getattr__(self, name: str) -> str: return ""
    Fore = DummyStyle(); Style = DummyStyle()


# --- Constants and Globals ---
ANSI_ESCAPE_PATTERN = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])') # Keep for cleaning file logs
# LOGGED_MESSAGES, _log_lock, LOG_LINE_HEURISTIC_PATTERN, LITELLM_ERROR_PATTERN are no longer needed if interceptor is removed

# Log level mapping
LOG_LEVEL_MAP: Dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
DEFAULT_LOG_LEVEL_NAME = "INFO"
APP_LOGGER_NAME = "promptweaver" # Base name for your application logs


# --- Log Symbols ---
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
    MODEL = "🤖" # Used for 'crew' logs


# --- Formatters ---
class ConsoleFormatter(logging.Formatter):
    """Applies fancy formatting to app logs, simple to others."""

    LEVEL_COLORS: Dict[int, str] = { # Correct Dict definition
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }
    LEVEL_SYMBOLS: Dict[int, str] = { # Correct Dict definition
        logging.DEBUG: LogSymbols.DEBUG,
        logging.INFO: LogSymbols.INFO,
        logging.WARNING: LogSymbols.WARNING,
        logging.ERROR: LogSymbols.ERROR,
        logging.CRITICAL: LogSymbols.CRITICAL,
    }
    # Ensure this calculation uses a dict, not a set
    MAX_LEVEL_LEN = max(len(logging.getLevelName(level)) for level in LEVEL_COLORS.keys())
    SIMPLE_CONSOLE_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def __init__(
        self,
        fmt='%(asctime)s │ %(levelname)s │ %(name)-15s │ %(message)s',
        datefmt='%H:%M:%S', # Default date format
        style='%',
    ):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.app_name_prefix = APP_LOGGER_NAME + "."
        self.app_name_exact = APP_LOGGER_NAME
        self._simple_formatter = logging.Formatter(fmt=self.SIMPLE_CONSOLE_FMT, datefmt=self.datefmt)

    def is_app_log(self, record: logging.LogRecord) -> bool:
        """Check if the log record is from our application."""
        return record.name == self.app_name_exact or record.name.startswith(self.app_name_prefix)

    def format(self, record: logging.LogRecord) -> str:
        # Use getMessage() for proper formatting of message arguments
        try: original_msg = record.getMessage()
        except Exception: original_msg = str(record.msg)

        # --- Fancy Formatting for App Logs ---
        if self.is_app_log(record):
            # Use a temporary attribute name that's less likely to clash
            if hasattr(record, '_np_console_formatted'): return super().format(record)

            log_color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
            # Get original level name string
            level_name_str = logging.getLevelName(record.levelno)
            # Calculate padding based on string length
            padding = ' ' * (self.MAX_LEVEL_LEN - len(level_name_str))
            # Format level name with color and padding
            record.levelname = f"{log_color}{level_name_str}{padding}{Style.RESET_ALL}"

            log_symbol = self.LEVEL_SYMBOLS.get(record.levelno, "")

            # Add symbols based on hints - use original_msg for checks
            current_msg = original_msg # Start with the original formatted message
            if 'API' in record.name: current_msg = f"{LogSymbols.API} {original_msg}"
            # Check for base app logger name or crew module name for MODEL symbol
            elif record.name == APP_LOGGER_NAME or record.name.startswith(APP_LOGGER_NAME + ".crew"):
                 current_msg = f"{LogSymbols.MODEL} {original_msg}"
            elif 'test' in record.name: current_msg = f"{LogSymbols.TEST} {original_msg}"
            else: current_msg = f"{log_symbol} {original_msg}"


            # Temporarily replace msg for formatting by parent
            # Save original args to restore later
            original_args = record.args
            record.msg = current_msg
            record.args = [] # Clear args as message is now pre-formatted string

            record._np_console_formatted = True
            formatted_message = super().format(record) # Use the main fmt string defined in __init__

            # Restore original values
            # Restore levelname to its original string value
            record.levelname = logging.getLevelName(record.levelno) # Get original level name string
            record.msg = original_msg # Restore original msg object
            record.args = original_args # Restore original args
            delattr(record, '_np_console_formatted')

            return formatted_message
        else:
            # --- Simple Formatting for Other Library Logs ---
            return self._simple_formatter.format(record)


class FileFormatter(logging.Formatter):
    """Applies symbol formatting to app logs, simple to others, always cleans ANSI."""

    LEVEL_SYMBOLS: Dict[int, str] = ConsoleFormatter.LEVEL_SYMBOLS # Reuse symbols from ConsoleFormatter
    MAX_LEVEL_LEN = ConsoleFormatter.MAX_LEVEL_LEN # Reuse max length
    SIMPLE_FILE_FMT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    def __init__(
        self,
        fmt='%(asctime)s │ %(levelname)-9s │ %(name)-15s │ %(message)s',
        datefmt='%H:%M:%S', # Default date format
        style='%',
    ):
         super().__init__(fmt=fmt, datefmt=datefmt, style=style)
         self.app_name_prefix = APP_LOGGER_NAME + "."
         self.app_name_exact = APP_LOGGER_NAME
         self._simple_formatter = logging.Formatter(fmt=self.SIMPLE_FILE_FMT, datefmt=self.datefmt)


    def is_app_log(self, record: logging.LogRecord) -> bool:
        """Check if the log record is from our application."""
        return record.name == self.app_name_exact or record.name.startswith(self.app_name_prefix)

    def format(self, record: logging.LogRecord) -> str:
        # Use getMessage() for proper formatting of message arguments
        try: original_msg = record.getMessage()
        except Exception: original_msg = str(record.msg)


        if self.is_app_log(record):
             # --- Symbol Formatting for App Logs in File ---
             if hasattr(record, '_np_file_formatted'):
                 formatted_message = super().format(record)
                 return ANSI_ESCAPE_PATTERN.sub('', formatted_message) # Clean ANSI

             # Get original level name string
             level_name_str = logging.getLevelName(record.levelno)
             # Calculate padding based on string length
             padding = ' ' * (self.MAX_LEVEL_LEN - len(level_name_str))
             # Format level name with padding
             record.levelname = f"{level_name_str}{padding}"

             log_symbol = self.LEVEL_SYMBOLS.get(record.levelno, "")
             current_msg = original_msg # Start with original

             # Add symbols based on hints
             if 'API' in record.name: current_msg = f"{LogSymbols.API} {original_msg}"
             elif record.name == APP_LOGGER_NAME or record.name.startswith(APP_LOGGER_NAME + ".crew"): current_msg = f"{LogSymbols.MODEL} {original_msg}"
             elif 'test' in record.name: current_msg = f"{LogSymbols.TEST} {original_msg}"
             else: current_msg = f"{log_symbol} {original_msg}"


             # Temporarily replace msg for formatting by parent
             original_args = record.args
             record.msg = current_msg
             record.args = []

             record._np_file_formatted = True
             formatted_message = super().format(record) # Use main fmt defined in __init__

             # Restore original values
             record.levelname = logging.getLevelName(record.levelno) # Restore original level name string
             record.msg = original_msg
             record.args = original_args
             delattr(record, '_np_file_formatted')

             # Clean ANSI just in case and return
             return ANSI_ESCAPE_PATTERN.sub('', formatted_message)
        else:
            # --- Simple Formatting for Other Library Logs in File ---
            formatted_message = self._simple_formatter.format(record)
            return ANSI_ESCAPE_PATTERN.sub('', formatted_message) # Clean ANSI just in case


# --- StdoutInterceptor (REMOVED - Not used if interception disabled by default) ---
# class StdoutInterceptor(io.TextIOBase): ...


# --- Logger Setup Class ---
class Logger:
    """Sets up application logging based on environment variables."""
    _is_setup = False
    _app_logger_instance: Optional[logging.Logger] = None # Store app logger instance

    # --- Configuration Options ---
    ENV_VAR_LOG_LEVEL = "LOG_LEVEL"
    ENV_VAR_LOG_FILE_ENABLE = "LOG_FILE_ENABLE"
    ENV_VAR_LOG_FILE_PATH = "LOG_FILE_PATH"
    # ENV_VAR_LOG_INTERCEPT is no longer used for setup directly

    # --- Defaults ---
    DEFAULT_LOG_LEVEL = logging.INFO
    DEFAULT_FILE_ENABLE = True
    # Interception is disabled by default, no ENV var needed to disable

    @staticmethod
    def get_default_log_file() -> Path:
        """Gets the default log file path."""
        try:
            # Assumes logger.py is in src/utils/, project root is two levels up
            project_root = Path(__file__).resolve().parent.parent.parent
        except NameError:
             project_root = Path(".").resolve() # Fallback if __file__ not defined (e.g., interactive)
        log_dir = project_root / "logs"
        try: log_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # Use original stderr/stdout for this error message
            print(f"[ERROR] Logger Setup: Could not create log directory '{log_dir}': {e}", file=sys.__stderr__)
            log_dir = Path(".")
        return log_dir / f"promptweaver_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    @staticmethod
    def setup() -> logging.Logger:
        """
        Configures logging handlers primarily for the application's namespace.
        Reads configuration from Environment Variables. Disables interception.
        Returns the application's base logger instance ('promptweaver').
        """
        if Logger._is_setup:
            # Return existing logger if setup already ran
            return Logger._app_logger_instance

        # --- Read Configuration from Environment Variables ---
        log_level_name = os.getenv(Logger.ENV_VAR_LOG_LEVEL, DEFAULT_LOG_LEVEL_NAME).upper()
        log_level = LOG_LEVEL_MAP.get(log_level_name, Logger.DEFAULT_LOG_LEVEL)
        log_file_enable = os.getenv(Logger.ENV_VAR_LOG_FILE_ENABLE, str(Logger.DEFAULT_FILE_ENABLE)).lower() == "true"
        log_file_path_override = os.getenv(Logger.ENV_VAR_LOG_FILE_PATH, None)
        # Interception is hardcoded to disabled here
        intercept_streams = False # Explicitly disabled

        # --- Configure Root Logger (Level Only) ---
        # Set level on root so libraries inherit it unless overridden
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        # Clear any default/existing handlers on root to prevent duplication/default formatting
        for handler in root_logger.handlers[:]:
             root_logger.removeHandler(handler)

        # --- Configure APPLICATION Logger ---
        app_logger = logging.getLogger(APP_LOGGER_NAME)
        app_logger.setLevel(log_level) # App logger respects the determined level
        app_logger.propagate = False # Crucial: Prevent app logs going to root

        # Clear any handlers potentially attached to the app logger from previous runs (e.g., during tests)
        for handler in app_logger.handlers[:]: app_logger.removeHandler(handler)

        # --- Define Formats ---
        console_fmt = '%(asctime)s │ %(levelname)s │ %(name)-15s │ %(message)s'
        file_fmt = '%(asctime)s │ %(levelname)-9s │ %(name)-15s │ %(message)s'
        # Define the date format string
        date_fmt = '%H:%M:%S'

        # --- Console Handler (Attached to App Logger) ---
        # Use original stdout for handler output itself
        console_handler = logging.StreamHandler(sys.stdout)
        # Use the variables defined above
        console_handler.setFormatter(ConsoleFormatter(fmt=console_fmt, datefmt=date_fmt))
        app_logger.addHandler(console_handler)

        # --- File Handler (Attached to App Logger, Conditional) ---
        actual_log_file = None
        if log_file_enable:
            if log_file_path_override:
                actual_log_file = Path(log_file_path_override)
                try:
                    actual_log_file.parent.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    print(f"[ERROR] Logger Setup: Could not create directory for log file '{actual_log_file}': {e}", file=sys.__stderr__)
                    actual_log_file = None # Disable file logging if dir fails
            else:
                actual_log_file = Logger.get_default_log_file()

        if actual_log_file:
            try:
                file_handler = logging.FileHandler(str(actual_log_file), encoding='utf-8', delay=True)
                # Use the variables defined above
                file_handler.setFormatter(FileFormatter(fmt=file_fmt, datefmt=date_fmt))
                app_logger.addHandler(file_handler)
                # Use print to original stdout/stderr for initial messages before potential interception
                print(f"{LogSymbols.INFO} Logging '{APP_LOGGER_NAME}' logs to file: {actual_log_file}", file=sys.stdout)
            except Exception as e:
                print(f"[ERROR] Logger Setup: Could not create log file handler for '{actual_log_file}': {e}", file=sys.__stderr__)
        elif log_file_enable:
             print(f"{LogSymbols.INFO} App file logging is disabled (no valid path/config).", file=sys.stdout)
        else:
             # File logging is disabled by config and no path override was given
             pass # No message needed, it's the default state if enabled=false

        # --- Stream Interception (Disabled) ---
        # The interceptor class is removed, so interception is off.
        # We explicitly state this state in the logs.
        print(f"{LogSymbols.INFO} Stdout/stderr interception is disabled.", file=sys.stdout)

        # --- Configure Library Log Levels ---
        LIB_LOG_LEVEL_NAME = os.getenv("LIBRARY_LOG_LEVEL", "WARNING").upper()
        LIB_LOG_LEVEL = LOG_LEVEL_MAP.get(LIB_LOG_LEVEL_NAME, logging.WARNING)
        # List common libraries that might log
        libraries_to_adjust = ["httpx", "LiteLLM", "openai", "crewai", "chromadb", "docling"]
        print(f"{LogSymbols.INFO} Setting log level for libraries {libraries_to_adjust} to {LIB_LOG_LEVEL_NAME}.", file=sys.stdout)
        for lib_name in libraries_to_adjust:
            lib_logger = logging.getLogger(lib_name)
            lib_logger.setLevel(LIB_LOG_LEVEL)
            # Ensure libraries don't add their own handlers if we cleared root
            # This also ensures library logs don't get the 'root' formatter from our setup
            lib_logger.handlers.clear()
            # Make sure they don't propagate up if root has no handlers now
            lib_logger.propagate = False


        # --- Log Startup Message (using the app logger) ---
        startup_logger = logging.getLogger(APP_LOGGER_NAME) # Use app logger
        divider = f"{LogSymbols.DIVIDER * 60}"
        startup_logger.info(divider)
        # Use the defined log_level_name variable
        startup_logger.info(f"Logger Setup Complete (App Level: {log_level_name}) {LogSymbols.SUCCESS}")
        startup_logger.info(f"File Logging (for '{APP_LOGGER_NAME}'): {'Enabled (' + str(actual_log_file) + ')' if actual_log_file else 'Disabled'}")
        # Explicitly state interception is disabled in startup log
        startup_logger.info(f"Stream Interception: Disabled")
        startup_logger.info(f"Library Log Level: {LIB_LOG_LEVEL_NAME}")
        startup_logger.info(divider)

        Logger._is_setup = True
        Logger._app_logger_instance = app_logger # Store app logger instance
        return app_logger # Return the main app logger

# --- get_logger Function ---
def get_logger(name: str) -> logging.Logger:
    """Gets a logger instance under the application's namespace, ensuring setup has run."""
    # Auto-setup with environment/defaults if accessed first
    if not Logger._is_setup:
        Logger.setup()

    # Construct logger name within the app namespace
    # Handle entry point script specifically (__main__)
    if name == "__main__":
        logger_name = f"{APP_LOGGER_NAME}.main"
    # Check if the name already starts with the app name and a dot (e.g., 'promptweaver.crew')
    elif name.startswith(APP_LOGGER_NAME + "."):
        logger_name = name
    # Handle the base app logger name itself ('promptweaver')
    elif name == APP_LOGGER_NAME:
        logger_name = APP_LOGGER_NAME
    else:
        # Append app name prefix if it's likely a module name like 'crew' or 'api'
        module_base_name = name.split('.')[-1]
        logger_name = f"{APP_LOGGER_NAME}.{module_base_name}"

    return logging.getLogger(logger_name)

# --- restore_stdout_stderr Function (Handles cleaning up saved attributes) ---
# This function remains, but it will only do anything if interception was previously *enabled*
# in a way that saved _original_stdout/_stderr.
def restore_stdout_stderr():
    """Restores original stdout and stderr streams if they were intercepted."""
    restored = False
    # Use original streams saved during setup (if interception was enabled)
    original_stdout = getattr(sys, '_original_stdout', None)
    original_stderr = getattr(sys, '_original_stderr', None)

    # Check if the current stream is NOT the original (implying it was replaced)
    # Avoid referencing StdoutInterceptor class as it might not be defined
    if original_stdout and sys.stdout is not original_stdout:
        sys.stdout = original_stdout
        if hasattr(sys, '_original_stdout'): del sys._original_stdout
        restored = True

    if original_stderr and sys.stderr is not original_stderr:
        sys.stderr = original_stderr
        if hasattr(sys, '_original_stderr'): del sys._original_stderr
        restored = True

    # Use the potentially restored stdout to print confirmation
    if restored:
        # Use the absolute original stream if possible for this message
        # Avoid using the logger itself here to prevent recursion
        print(f"{LogSymbols.INFO} Restored original stdout/stderr.", file=sys.__stdout__)