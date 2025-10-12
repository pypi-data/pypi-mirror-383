cmake_minimum_required(VERSION 3.20.0)

# Create the nanobind module for oven-opt
nanobind_add_module(
  oven_opt_py
  NB_STATIC
  oven_opt_bindings.cpp
)

# Get all MLIR libraries to avoid missing symbols
get_property(mlir_libs GLOBAL PROPERTY MLIR_ALL_LIBS)

# Link against all MLIR libraries
target_link_libraries(oven_opt_py PRIVATE
  # All MLIR libraries to avoid missing symbols
  ${mlir_libs}
  
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