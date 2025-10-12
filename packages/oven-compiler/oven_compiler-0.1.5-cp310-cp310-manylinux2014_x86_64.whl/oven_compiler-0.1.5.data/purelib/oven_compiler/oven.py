"""
Oven MLIR Compiler Python Interface

This module provides a high-level Python interface for the Oven MLIR compiler,
allowing you to optimize and compile MLIR code directly from Python.
"""

try:
    from .oven_opt_py import (
        OvenOptimizer,
        optimize_string,
        optimize_file,
        to_llvm_ir,
        to_ptx,
        optimize_and_convert,
    )
except ImportError:
    # Fallback if the module is not built yet
    class OvenOptimizer:
        def __init__(self):
            raise ImportError(
                "oven_opt_py native module not found. Please build the project first."
            )

    def optimize_string(code):
        raise ImportError(
            "oven_opt_py native module not found. Please build the project first."
        )

    def optimize_file(filename):
        raise ImportError(
            "oven_opt_py native module not found. Please build the project first."
        )

    def to_llvm_ir(code):
        raise ImportError(
            "oven_opt_py native module not found. Please build the project first."
        )

    def to_ptx(code):
        raise ImportError(
            "oven_opt_py native module not found. Please build the project first."
        )

    def optimize_and_convert(code, format):
        raise ImportError(
            "oven_opt_py native module not found. Please build the project first."
        )


import tempfile
import os
from pathlib import Path


class OvenCompiler:
    """
    High-level interface for Oven MLIR compilation.
    """

    def __init__(self):
        self.optimizer = OvenOptimizer()

    def compile_string(self, mlir_code, output_format="mlir"):
        """
        Compile MLIR code string to the specified output format.

        Args:
            mlir_code (str): MLIR code to compile
            output_format (str): 'mlir' for optimized MLIR, 'llvm' for LLVM IR, 'ptx' for PTX assembly

        Returns:
            str: Compiled code in the requested format
        """
        return self.optimizer.optimize_and_convert(mlir_code, output_format.lower())

    def compile_file(self, input_file, output_file=None, output_format="mlir"):
        """
        Compile MLIR file to the specified output format.

        Args:
            input_file (str): Path to input MLIR file
            output_file (str, optional): Path to output file. If None, returns as string
            output_format (str): 'mlir' for optimized MLIR, 'llvm' for LLVM IR, 'ptx' for PTX assembly

        Returns:
            str or None: If output_file is None, returns compiled code as string
        """
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Read input file
        with open(input_path, "r") as f:
            mlir_code = f.read()

        # Compile using the new optimize_and_convert method
        result = self.optimizer.optimize_and_convert(mlir_code, output_format.lower())

        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(result)
            return None
        else:
            return result

    def compile_to_ptx(self, mlir_code, output_file=None):
        """
        Compile MLIR code to PTX assembly.
        Note: This requires additional LLVM tools to be available.

        Args:
            mlir_code (str): MLIR code to compile
            output_file (str, optional): Path to output PTX file

        Returns:
            str: PTX assembly code
        """
        # First convert to LLVM IR
        llvm_ir = self.optimizer.to_llvm_ir(mlir_code)

        if llvm_ir.startswith("Error:"):
            return llvm_ir

        # Use temporary files for LLVM compilation
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ll", delete=False
        ) as llvm_file:
            llvm_file.write(llvm_ir)
            llvm_file_path = llvm_file.name

        try:
            # Compile LLVM IR to PTX using llc
            if output_file:
                ptx_path = output_file
            else:
                ptx_path = llvm_file_path.replace(".ll", ".ptx")

            import subprocess

            cmd = [
                "llc",
                "-march=nvptx64",
                "-mcpu=sm_75",  # Adjust based on your GPU
                "-o",
                ptx_path,
                llvm_file_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                return f"Error compiling to PTX: {result.stderr}"

            # Read the PTX file
            with open(ptx_path, "r") as f:
                ptx_code = f.read()

            if not output_file:
                os.unlink(ptx_path)  # Clean up temporary PTX file

            return ptx_code

        finally:
            os.unlink(llvm_file_path)  # Clean up temporary LLVM file


def compile_oven_mlir(input_file, output_file=None, format="mlir"):
    """
    Convenience function to compile Oven MLIR files.

    Args:
        input_file (str): Path to input MLIR file
        output_file (str, optional): Path to output file
        format (str): Output format ('mlir', 'llvm', 'ptx')

    Returns:
        str or None: Compiled code if output_file is None
    """
    compiler = OvenCompiler()

    if format.lower() == "ptx":
        with open(input_file, "r") as f:
            mlir_code = f.read()
        result = compiler.compile_to_ptx(mlir_code, output_file)
        if output_file:
            return None
        return result
    else:
        return compiler.compile_file(input_file, output_file, format)


# Export public API
__all__ = [
    "OvenCompiler",
    "OvenOptimizer",
    "compile_oven_mlir",
    "optimize_string",
    "optimize_file",
    "to_llvm_ir",
]
