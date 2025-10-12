"""
Integrated Python to PTX Compiler

This module provides a complete pipeline for compiling Python code to PTX assembly
through MLIR using oven-compiler (Python → MLIR) and oven-compiler (MLIR → PTX).
"""

from typing import Optional, Dict, Any
import tempfile
import os
from pathlib import Path

try:
    from oven.compiler import PythonToMLIRCompiler

    _OVEN_COMPILER_AVAILABLE = True
except ImportError:
    _OVEN_COMPILER_AVAILABLE = False

try:
    from .oven import OvenCompiler

    _OVEN_COMPILER_AVAILABLE = True
except ImportError:
    try:
        from oven_compiler.oven import OvenCompiler

        _OVEN_COMPILER_AVAILABLE = True
    except ImportError:
        _OVEN_COMPILER_AVAILABLE = False


class PythonToPTXCompiler:
    """
    Integrated compiler that combines oven-compiler (Python → MLIR)
    with oven-compiler (MLIR → PTX) for complete Python to PTX compilation.
    """

    def __init__(self):
        """Initialize both compilers."""
        try:
            from oven import PythonToMLIRCompiler

            self.python_compiler = PythonToMLIRCompiler()

        except ImportError as e:
            raise RuntimeError(f"Required dependencies not available: {e}")

    def get_compiler_info(self) -> dict:
        """Get information about both compilers."""
        from . import __version__

        return {
            "python_compiler": {
                "name": "oven-compiler",
                "version": __version__,
                "capabilities": ["Python", "AST", "MLIR"],
            },
            "mlir_compiler": {
                "name": "oven-compiler",
                "capabilities": ["MLIR", "LLVM IR", "PTX"],
            },
            "pipeline": "Python → MLIR → LLVM IR → PTX Assembly",
        }

    def compile_python_to_ptx(self, python_code: str) -> str:
        """
        Compile Python source code directly to PTX assembly.

        Args:
            python_code: Python source code as string

        Returns:
            str: Generated PTX assembly code

        Raises:
            RuntimeError: If compilation fails at any stage
        """
        try:
            # Step 1: Python → MLIR
            mlir_code = self.python_compiler.compile_source(python_code)
            if self.python_compiler.compilation_errors:
                errors = self.python_compiler.get_compilation_errors()
                raise RuntimeError(f"Python to MLIR compilation failed: {errors}")

            # Step 2: MLIR → PTX (using module-level function)
            from . import to_ptx

            ptx_code = to_ptx(mlir_code)
            return ptx_code

        except Exception as e:
            raise RuntimeError(f"Python to PTX compilation failed: {str(e)}")

    def compile_python_file_to_ptx(self, python_file: str) -> str:
        """
        Compile Python file to PTX assembly.

        Args:
            python_file: Path to Python source file

        Returns:
            str: Generated PTX assembly code
        """
        try:
            # Step 1: Python file → MLIR
            mlir_code = self.python_compiler.compile_file(python_file)
            if self.python_compiler.compilation_errors:
                errors = self.python_compiler.get_compilation_errors()
                raise RuntimeError(f"Python to MLIR compilation failed: {errors}")

            # Step 2: MLIR → PTX
            from . import to_ptx

            ptx_code = to_ptx(mlir_code)
            return ptx_code

        except Exception as e:
            raise RuntimeError(f"Python file to PTX compilation failed: {str(e)}")

    def compile_with_intermediate_files(
        self, python_code: str, output_dir: str = "."
    ) -> dict:
        """
        Compile Python to PTX and save intermediate files.

        Args:
            python_code: Python source code
            output_dir: Directory to save intermediate files

        Returns:
            dict: Paths to generated files
        """
        import os

        try:
            # Step 1: Python → MLIR
            mlir_code = self.python_compiler.compile_source(python_code)
            if self.python_compiler.compilation_errors:
                errors = self.python_compiler.get_compilation_errors()
                raise RuntimeError(f"Python to MLIR compilation failed: {errors}")

            # Save MLIR
            mlir_file = os.path.join(output_dir, "intermediate.mlir")
            with open(mlir_file, "w") as f:
                f.write(mlir_code)

            # Step 2: MLIR → LLVM IR
            from . import to_llvm_ir

            llvm_ir = to_llvm_ir(mlir_code)
            llvm_file = os.path.join(output_dir, "intermediate.ll")
            with open(llvm_file, "w") as f:
                f.write(llvm_ir)

            # Step 3: LLVM IR → PTX
            from . import to_ptx

            ptx_code = to_ptx(mlir_code)
            ptx_file = os.path.join(output_dir, "output.ptx")
            with open(ptx_file, "w") as f:
                f.write(ptx_code)

            return {
                "mlir": mlir_file,
                "llvm_ir": llvm_file,
                "ptx": ptx_file,
                "mlir_code": mlir_code,
                "llvm_ir_code": llvm_ir,
                "ptx_code": ptx_code,
            }

        except Exception as e:
            raise RuntimeError(f"Compilation with intermediate files failed: {str(e)}")

    def compile_python_file_to_ptx(
        self, input_file: str, output_file: Optional[str] = None
    ) -> str:
        """
        Compile a Python file directly to PTX assembly.

        Args:
            input_file: Path to Python source file
            output_file: Optional output PTX file path

        Returns:
            str: Generated PTX assembly code
        """
        # Read Python source
        with open(input_file, "r", encoding="utf-8") as f:
            python_code = f.read()

        # Compile using our main method
        ptx_code = self.compile_python_to_ptx(python_code)

        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(ptx_code)


# Convenience functions
def compile_python_string_to_ptx(python_code: str) -> str:
    """
    Convenience function to compile Python string to PTX.

    Args:
        python_code: Python source code

    Returns:
        PTX assembly code
    """
    compiler = PythonToPTXCompiler()
    return compiler.compile_python_to_ptx(python_code)


def compile_python_file_to_ptx(input_file: str, output_file: str = None) -> str:
    """
    Convenience function to compile Python file to PTX.

    Args:
        input_file: Input Python file path
        output_file: Output PTX file path (optional)

    Returns:
        PTX assembly code
    """
    compiler = PythonToPTXCompiler()
    return compiler.compile_python_file_to_ptx(input_file)
