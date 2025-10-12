cmake_minimum_required(VERSION 3.20.0)

# Create the nanobind module for oven-opt
nanobind_add_module(
  oven_opt_py
  NB_STATIC
  oven_opt_bindings.cpp
)

# Add compiler flags for size optimization
target_compile_options(oven_opt_py PRIVATE
  -Os  # Optimize for size
  -ffunction-sections
  -fdata-sections
)

# Add linker flags for size optimization
target_link_options(oven_opt_py PRIVATE
  -Wl,--gc-sections  # Remove unused sections
  -Wl,--strip-all    # Strip all symbols
)

# Get essential MLIR libraries only
set(essential_mlir_libs
  MLIRParser
  MLIRPass
  MLIRTransforms
  MLIRTargetLLVMIRExport
  MLIRExecutionEngine
  MLIRLLVMToLLVMIRTranslation
  MLIRNVVMToLLVMIRTranslation
  MLIRIR
  MLIRSupport
)

# Link against essential libraries only
target_link_libraries(oven_opt_py PRIVATE
  # Essential MLIR libraries only
  ${essential_mlir_libs}
  
  # Oven specific libraries (use target names instead of paths)
  MLIROven
  OvenPasses
  OvenToLLVM
  AddNVVMKernel
)

# Add include directories
target_include_directories(oven_opt_py PRIVATE
  ${PROJECT_SOURCE_DIR}
  ${PROJECT_SOURCE_DIR}/lib
  ${LLVM_INCLUDE_DIRS}
  ${MLIR_INCLUDE_DIRS}
)

# Set installation directory
install(TARGETS oven_opt_py LIBRARY DESTINATION .)