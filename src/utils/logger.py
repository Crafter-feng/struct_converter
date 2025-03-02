from typing import Optional
from loguru import logger
from config import LoggingConfig

__all__ = ['logger']



logger.add("logs/debug.log", level="DEBUG", mode='w')