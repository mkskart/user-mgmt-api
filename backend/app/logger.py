"""Centralised Loguru configuration with coloured console output."""
import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> \u00BB "
    "<level>{message}</level>",
    colorize=True,
    backtrace=False,
    diagnose=False,
)

__all__ = ["logger"]