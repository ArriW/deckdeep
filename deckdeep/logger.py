import logging
from logging.handlers import RotatingFileHandler
from colorama import init, Fore, Style
import os
import time

# Initialize colorama
init(autoreset=True)


class CategoryColoredFormatter(logging.Formatter):
    CATEGORY_COLORS = {
        "RENDER": Fore.CYAN,
        "COMBAT": Fore.RED,
        "EVENT": Fore.YELLOW,
        "SYSTEM": Fore.GREEN,
        "PLAYER": Fore.MAGENTA,
        "ASSET": Fore.LIGHTBLUE_EX,
        "PERFORMANCE": Fore.LIGHTGREEN_EX,
    }
    DEFAULT_COLOR = Fore.WHITE

    def format(self, record):
        log_message = super().format(record)
        if hasattr(record, "category"):
            color = self.CATEGORY_COLORS.get(
                getattr(record, "category", "").upper(), self.DEFAULT_COLOR
            )
        else:
            color = self.DEFAULT_COLOR
        return f"{color}{log_message}{Style.RESET_ALL}"


class GameLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self.categories = set()
        self.timers = {}

    def log(self, level, msg, category=None, *args, **kwargs):
        if category:
            self.categories.add(category.upper())
            extra = kwargs.get("extra", {})
            extra["category"] = category.upper()
            kwargs["extra"] = extra
            msg = f"[{category.upper()}] {msg}"
        super().log(level, msg, *args, **kwargs)

    def info(self, msg, category=None, *args, **kwargs):
        self.log(logging.INFO, msg, category, *args, **kwargs)

    def error(self, msg, category=None, *args, **kwargs):
        if "exc_info" not in kwargs:
            kwargs["exc_info"] = True
        self.log(logging.ERROR, msg, category, *args, **kwargs)

    def debug(self, msg, category=None, *args, **kwargs):
        self.log(logging.DEBUG, msg, category, *args, **kwargs)

    def warning(self, msg, category=None, *args, **kwargs):
        self.log(logging.WARNING, msg, category, *args, **kwargs)

    def start_timer(self, name):
        self.timers[name] = time.time()

    def stop_timer(self, name, category="PERFORMANCE"):
        if name not in self.timers:
            self.warning(f"Timer '{name}' not found", category=category)
            return
        elapsed = time.time() - self.timers[name]
        self.info(
            f"Timer '{name}' completed in {elapsed:.4f} seconds", category=category
        )
        del self.timers[name]

    def log_player_action(self, action, details=None):
        msg = f"Player Action: {action}"
        if details:
            msg += f" - Details: {details}"
        self.info(msg, category="PLAYER")

    def log_asset_load(self, asset_name, status):
        self.info(f"Asset Load: {asset_name} - Status: {status}", category="ASSET")


def setup_game_logger(
    name="game_logger", level=logging.DEBUG, log_file="game.log", max_lines=10000
):
    logger = GameLogger(name, level)

    # Console Handler with colored output and simplified timestamp
    console_formatter = CategoryColoredFormatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )  # Only show time
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler with simplified timestamp
    file_formatter = logging.Formatter(
        # "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )  # Show date and time, but no milliseconds
    max_bytes = max_lines * 100
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=1)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


# Usage example
if __name__ == "__main__":
    logger = setup_game_logger()

    logger.info("Game starting", category="SYSTEM")

    logger.start_timer("level_load")
    logger.log_asset_load("player_model.fbx", "Loading")
    time.sleep(1)  # Simulate some work
    logger.log_asset_load("player_model.fbx", "Loaded")
    logger.stop_timer("level_load")

    logger.log_player_action("Jump", "Height: 3 units")

    try:
        1 / 0
    except Exception:
        logger.error("Division by zero error", category="COMBAT")

    print("\nCategories used:", logger.categories)
    print(f"Log file created: {os.path.abspath('game.log')}")
