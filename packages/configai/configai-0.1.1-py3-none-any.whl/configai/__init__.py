"""
ConfigAI - PyTorch to HLS Deployment Compiler
Powered by Stream-HLS
Author: Ayush Kumar (aykumar)
"""

__version__ = "0.1.1"

from .compiler import compile_model
from .model_wrapper import ConfigAIModel

__all__ = ['compile_model', 'ConfigAIModel']
