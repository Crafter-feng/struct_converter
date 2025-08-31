from typing import Optional
from loguru import logger

__all__ = ['logger']



logger.add("logs/debug.log", level="ERROR", mode='w')