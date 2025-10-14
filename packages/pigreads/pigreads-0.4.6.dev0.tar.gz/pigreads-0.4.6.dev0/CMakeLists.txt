cmake_minimum_required(VERSION 3.15...3.26)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 CONFIG REQUIRED)
find_package(OpenCL REQUIRED)

pybind11_add_module(core1 MODULE src/core1/main.cpp)
pybind11_add_module(core2 MODULE src/core2/main.cpp)

target_link_libraries(core1 PRIVATE OpenCL::OpenCL)
target_link_libraries(core2 PRIVATE OpenCL::OpenCL)
set_target_properties(
  core1
  PROPERTIES C_STANDARD 11
             C_STANDARD_REQUIRED ON
             C_EXTENSIONS OFF)
set_target_properties(
  core2
  PROPERTIES C_STANDARD 11
             C_STANDARD_REQUIRED ON
             C_EXTENSIONS OFF)
target_compile_definitions(core1 PRIVATE CL_TARGET_OPENCL_VERSION=100)
target_compile_definitions(core2 PRIVATE CL_TARGET_OPENCL_VERSION=100)

install(TARGETS core1 core2 DESTINATION ${SKBUILD_PROJECT_NAME})
