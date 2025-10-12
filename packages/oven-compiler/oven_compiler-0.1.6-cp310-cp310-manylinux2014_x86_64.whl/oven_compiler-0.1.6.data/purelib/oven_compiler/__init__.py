"""
Oven MLIR Compiler - Python Bindings

This package provides Python bindings for the Oven MLIR compiler,
allowing seamless integration of MLIR compilation into Python workflows.

Example usage:

    import oven

    # Simple compilation
    compiler = oven.OvenCompiler()
    result = compiler.compile_file('my_kernel.mlir', format='llvm')

    # Or use convenience function
    llvm_ir = oven.compile_oven_mlir('my_kernel.mlir', format='llvm')

    # Direct nanobind access
    optimizer = oven.OvenOptimizer()
    result = optimizer.optimize_mlir(mlir_code)
"""

__version__ = "0.1.6"

# Import the native module
try:
    from .oven_opt_py import (
        OvenOptimizer,
        optimize_string,
        optimize_file,
        to_llvm_ir,
        to_ptx,
        optimize_and_convert,
        check_targets,
        check_ptx_support,
        get_compute_capability,
        set_compute_capability,
    )

    _NATIVE_MODULE_AVAILABLE = True
except ImportError as e:
    _NATIVE_MODULE_AVAILABLE = False
    _IMPORT_ERROR = str(e)

# Import high-level interface
if _NATIVE_MODULE_AVAILABLE:
    from .oven import OvenCompiler, compile_oven_mlir

    # Import integrated Python to PTX compiler
    try:
        from .python_to_ptx import (
            PythonToPTXCompiler,
            compile_python_string_to_ptx,
            compile_python_file_to_ptx,
        )

        _PYTHON_TO_PTX_AVAILABLE = True
    except ImportError:
        _PYTHON_TO_PTX_AVAILABLE = False

        # Create placeholder classes for missing dependencies
        class PythonToPTXCompiler:
            def __init__(self, *args, **kwargs):
                raise ImportError(
                    "oven-compiler dependency issue. Try reinstalling: pip install --force-reinstall oven-compiler"
                )

        def compile_python_string_to_ptx(*args, **kwargs):
            raise ImportError(
                "oven-compiler dependency issue. Try reinstalling: pip install --force-reinstall oven-compiler"
            )

        def compile_python_file_to_ptx(*args, **kwargs):
            raise ImportError(
                "oven-compiler dependency issue. Try reinstalling: pip install --force-reinstall oven-compiler"
            )

else:
    # Provide helpful error messages when native module is not available
    import platform as _platform

    _ERROR_MESSAGE = f"""
Native MLIR module not available: {_IMPORT_ERROR}

This usually happens when:
1. The package was installed without native modules (wheel not compatible with your platform)
2. Required system libraries are missing
3. The package was built for a different Python version

Solutions:
1. Install platform-specific wheel: pip install --force-reinstall --no-deps oven-compiler
2. For Python-to-PTX only: pip install oven-compiler
3. Build from source with MLIR support

Platform-specific wheels available for: linux_x86_64, macos_x86_64, win_amd64
Current platform: {_platform.platform()}
"""

    class _MissingNativeModule:
        def __init__(self, name):
            self.name = name

        def __call__(self, *args, **kwargs):
            raise ImportError(_ERROR_MESSAGE)

        def __getattr__(self, name):
            raise ImportError(_ERROR_MESSAGE)

    OvenOptimizer = _MissingNativeModule("OvenOptimizer")
    OvenCompiler = _MissingNativeModule("OvenCompiler")
    optimize_string = _MissingNativeModule("optimize_string")
    optimize_file = _MissingNativeModule("optimize_file")
    to_llvm_ir = _MissingNativeModule("to_llvm_ir")
    to_ptx = _MissingNativeModule("to_ptx")
    optimize_and_convert = _MissingNativeModule("optimize_and_convert")
    compile_oven_mlir = _MissingNativeModule("compile_oven_mlir")
    check_targets = _MissingNativeModule("check_targets")
    check_ptx_support = _MissingNativeModule("check_ptx_support")
    get_compute_capability = _MissingNativeModule("get_compute_capability")
    set_compute_capability = _MissingNativeModule("set_compute_capability")

# Export public API
__all__ = [
    # Core MLIR compilation
    "OvenOptimizer",
    "OvenCompiler",
    "optimize_string",
    "optimize_file",
    "to_llvm_ir",
    "to_ptx",
    "optimize_and_convert",
    "compile_oven_mlir",
    # Target checking
    "check_targets",
    "check_ptx_support",
    # Integrated Python to PTX compilation
    "PythonToPTXCompiler",
    "compile_python_string_to_ptx",
    "compile_python_file_to_ptx",
]
