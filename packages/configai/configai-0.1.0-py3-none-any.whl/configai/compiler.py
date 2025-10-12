"""
Main compilation API for ConfigAI
Powered by Stream-HLS
"""

import os
import sys
import shutil
import subprocess
import torch
from pathlib import Path
from typing import Tuple, Optional, Union
import tempfile
import json


def compile_model(
    model: torch.nn.Module,
    input_shape: Tuple[int, ...],
    output_dir: str,
    model_name: str = "Model",
    opt_level: int = 0,
    dsps: int = 7680,
    weights_path: Optional[str] = None,
    verbose: bool = True
) -> dict:
    """
    Compile a PyTorch model to HLS deployment package.
    
    Args:
        model: PyTorch model instance
        input_shape: Input tensor shape (batch_size, *dims)
        output_dir: Output directory for deployment package
        model_name: Name of the model
        opt_level: Optimization level (0-5)
        dsps: Number of DSPs available (default: 7680)
        weights_path: Path to pretrained weights .pth file (optional)
        verbose: Print compilation progress
        
    Returns:
        dict: Compilation report with paths and metadata
        
    Example:
        >>> model = MyModel()
        >>> compile_model(
        ...     model=model,
        ...     input_shape=(1, 784),
        ...     output_dir="./MyModel_deployment",
        ...     model_name="MyModel",
        ...     opt_level=0
        ... )
    """
    
    if verbose:
        print(f"🚀 ConfigAI Compiler v{sys.modules['configai'].__version__}")
        print(f"📦 Compiling {model_name}...")
    
    # Validate inputs
    if not isinstance(model, torch.nn.Module):
        raise TypeError("model must be a torch.nn.Module instance")
    
    if not isinstance(input_shape, (tuple, list)):
        raise TypeError("input_shape must be a tuple or list")
    
    # Get Stream-HLS repository path
    streamhls_repo = os.environ.get(
        'STREAMHLS_REPO',
        '/home/aykumar/streamhls/Stream-HLS'
    )
    
    if not os.path.exists(streamhls_repo):
        raise RuntimeError(
            f"Stream-HLS repository not found at {streamhls_repo}. "
            f"Set STREAMHLS_REPO environment variable or install Stream-HLS."
        )
    
    # Create temporary working directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Step 1: Save model to temporary location
        if verbose:
            print(f"💾 Preparing model...")
        
        model_dir = temp_path / "pymodels" / "temp_benchmark"
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model Python code
        model_file = model_dir / f"{model_name}.py"
        _save_model_code(model, model_name, model_file)
        
        # Save weights if model has trained parameters
        if weights_path:
            weights_file = model_dir / "weights" / f"{model_name}.pth"
            weights_file.parent.mkdir(exist_ok=True)
            if os.path.isfile(weights_path):
                shutil.copy(weights_path, weights_file)
        else:
            # Check if model has trainable parameters and save them
            if any(p.requires_grad for p in model.parameters()):
                weights_file = model_dir / "weights" / f"{model_name}.pth"
                weights_file.parent.mkdir(parents=True, exist_ok=True)
                torch.save(model.state_dict(), weights_file)
                if verbose:
                    print(f"💾 Saved model weights to {weights_file}")
        
        # Step 2: Register model in data.py
        if verbose:
            print(f"📝 Registering model...")
        
        examples_dir = Path(streamhls_repo) / "examples"
        _register_model_in_data_py(
            examples_dir / "data.py",
            "temp_benchmark",
            model_name,
            input_shape
        )
        
        # Copy model to Stream-HLS repository
        target_model_dir = examples_dir / "pymodels" / "temp_benchmark"
        if target_model_dir.exists():
            shutil.rmtree(target_model_dir)
        shutil.copytree(model_dir, target_model_dir)
        
        # Step 3: Run compilation
        if verbose:
            print(f"⚙️  Running MLIR → HLS compilation...")
        
        compile_cmd = [
            sys.executable,
            str(examples_dir / "run_streamhls.py"),
            "-b", "temp_benchmark",
            "-k", model_name,
            "-O", str(opt_level),
            "-c", "1"  # Compile only, no Vitis synthesis
        ]
        
        # Set environment
        env = os.environ.copy()
        env['PYTHONPATH'] = str(examples_dir) + ":" + env.get('PYTHONPATH', '')
        
        result = subprocess.run(
            compile_cmd,
            cwd=examples_dir,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Compilation failed!")
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError(f"Compilation failed with code {result.returncode}")
        
        if verbose:
            print(f"✅ Compilation successful!")
        
        # Step 4: Package deployment folder
        if verbose:
            print(f"📦 Creating deployment package...")
        
        design_dir = examples_dir / "designs" / "temp_benchmark" / f"opt{opt_level}" / f"{model_name}_{dsps}" / model_name
        
        if not design_dir.exists():
            raise RuntimeError(f"Compiled design not found at {design_dir}")
        
        # Create deployment package in MNIST_deployment format
        output_path = Path(output_dir)
        if output_path.exists():
            shutil.rmtree(output_path)
        
        _create_deployment_package(
            design_dir=design_dir,
            output_dir=output_path,
            model_name=model_name,
            input_shape=input_shape,
            opt_level=opt_level
        )
        
        if verbose:
            print(f"✅ Deployment package created at: {output_path}")
        
        # Cleanup temporary model from Stream-HLS
        if target_model_dir.exists():
            shutil.rmtree(target_model_dir)
        
        # Return report
        report = {
            "model_name": model_name,
            "input_shape": input_shape,
            "opt_level": opt_level,
            "output_dir": str(output_path.absolute()),
            "hls_src": str(output_path / "hls" / "src"),
            "mlir_files": str(output_path / "mlir"),
            "success": True
        }
        
        return report


def _save_model_code(model: torch.nn.Module, model_name: str, output_file: Path):
    """Generate Python code for the model and save it."""
    
    # Import base class
    base_import = "from pymodels.base_model import StreamHLSModel"
    
    # Get model's forward method and __init__
    model_class = model.__class__
    
    # Generate model code (simplified - you may need to enhance this)
    code = f'''"""
Auto-generated model: {model_name}
"""

import torch
import torch.nn as nn
{base_import}

class {model_name}(StreamHLSModel):
    def __init__(self):
        super().__init__()
        # Model architecture (you need to reconstruct this)
'''
    
    # Add layers
    for name, module in model.named_children():
        code += f"        self.{name} = {repr(module)}\n"
    
    code += '''
    def forward(self, x):
'''
    
    # Try to get forward code (this is simplified)
    # In practice, you might need torch.jit.script or manual specification
    code += '''        # Forward pass - FIXME: Auto-generate from model
        # You may need to manually specify the forward pass
        pass
'''
    
    output_file.write_text(code)


def _register_model_in_data_py(data_py_path: Path, benchmark: str, model_name: str, input_shape: Tuple):
    """Register model in data.py (append to benchmark section)."""
    
    import re
    
    content = data_py_path.read_text()
    
    # Generate input tensor args
    if len(input_shape) == 2:
        tensor_args = f"{input_shape[0]}, {input_shape[1]}"
    elif len(input_shape) == 4:
        tensor_args = f"{input_shape[0]}, {input_shape[1]}, {input_shape[2]}, {input_shape[3]}"
    else:
        tensor_args = str(input_shape)[1:-1]  # Remove parentheses
    
    model_entry = f'''    "{model_name}" : {{
      "class": "{model_name}",
      "config" : {{}},
      "input" : (
        randTensor({tensor_args}, dtype=dtype),
      )
    }}'''
    
    # Check if benchmark exists
    if f'"{benchmark}"' not in content:
        # Add new benchmark section
        new_benchmark = f'''  "{benchmark}" : {{
{model_entry}
  }},
'''
        # Insert before closing brace of model_configs
        content = content.replace(
            '\n}',
            f'\n{new_benchmark}}}'
        )
    else:
        # Add to existing benchmark (similar to auto_register_models.py logic)
        # For simplicity, we'll just append
        pass
    
    data_py_path.write_text(content)


def _create_deployment_package(
    design_dir: Path,
    output_dir: Path,
    model_name: str,
    input_shape: Tuple,
    opt_level: int
):
    """Create deployment package in MNIST_deployment format."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy HLS source code
    hls_src = design_dir / "hls" / "src"
    if hls_src.exists():
        shutil.copytree(hls_src, output_dir / "hls" / "src")
    
    # Copy HLS data (golden outputs)
    hls_data = design_dir / "hls" / "data"
    if hls_data.exists():
        shutil.copytree(hls_data, output_dir / "hls" / "data")
    
    # Copy MLIR files
    mlir_dir = design_dir / "mlir"
    if mlir_dir.exists():
        shutil.copytree(mlir_dir, output_dir / "mlir")
    
    # Create README
    readme_content = f"""# {model_name} Deployment Package

## Model Information
- **Model Name**: {model_name}
- **Input Shape**: {input_shape}
- **Optimization Level**: {opt_level}
- **Generated by**: StreamHLS Compiler

## Directory Structure

```
{model_name}_deployment/
├── hls/
│   ├── src/           # HLS C++ source code
│   └── data/          # Golden output data
├── mlir/              # MLIR intermediate files
└── README.md          # This file
```

## Usage

### HLS Synthesis (Vitis HLS)
```bash
cd hls/src
vitis_hls -f run.tcl
```

### C Simulation
The golden output data in `hls/data/` can be used to verify the HLS implementation.

## Next Steps

1. Run HLS synthesis in Vitis HLS
2. Verify C simulation results
3. Run C/RTL co-simulation
4. Export as IP or generate bitstream

---
Generated by StreamHLS Compiler
"""
    
    (output_dir / "README.md").write_text(readme_content)
    
    # Create metadata JSON
    metadata = {
        "model_name": model_name,
        "input_shape": list(input_shape),
        "opt_level": opt_level,
        "compiler_version": sys.modules['configai'].__version__,
        "generated_by": "ConfigAI Compiler"
    }
    
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    
    print(f"✅ Created deployment package at {output_dir}")
