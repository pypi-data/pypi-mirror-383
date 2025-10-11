"""
Yoruba TTS Package
"""

from .core import YorubaTTS, TTSOptions
from .models.model_manager import ModelManager

__version__ = "0.1.0"
__author__ = "LKK"
__all__ = ["YorubaTTS", "TTSOptions", "ModelManager"]