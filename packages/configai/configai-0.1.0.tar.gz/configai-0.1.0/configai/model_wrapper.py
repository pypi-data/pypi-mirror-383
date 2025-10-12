"""
ConfigAI Model wrapper for easy integration
"""

import torch
import torch.nn as nn
from typing import Tuple


class ConfigAIModel(nn.Module):
    """
    Base class for ConfigAI-compatible models.
    Automatically handles weight loading and provides compilation interface.
    """
    
    def __init__(self):
        super().__init__()
    
    def compile_to_hls(
        self,
        input_shape: Tuple[int, ...],
        output_dir: str,
        opt_level: int = 0,
        **kwargs
    ):
        """
        Compile this model to HLS deployment package.
        
        Args:
            input_shape: Input tensor shape
            output_dir: Output directory for deployment
            opt_level: Optimization level (0-5)
            **kwargs: Additional arguments passed to compile_model
        """
        from .compiler import compile_model
        
        model_name = self.__class__.__name__
        
        return compile_model(
            model=self,
            input_shape=input_shape,
            output_dir=output_dir,
            model_name=model_name,
            opt_level=opt_level,
            **kwargs
        )
