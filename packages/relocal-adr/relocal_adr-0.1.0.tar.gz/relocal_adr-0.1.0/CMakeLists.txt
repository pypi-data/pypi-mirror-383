cmake_minimum_required(VERSION 3.15)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX)

include(FetchContent)
FetchContent_Declare(
  ceres
  URL http://ceres-solver.org/ceres-solver-2.2.0.tar.gz
  URL_HASH SHA256=48b2302a7986ece172898477c3bcd6deb8fb5cf19b3327bc49969aad4cede82d
)
# 关键：关掉不需要的组件，省编译时间
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BUILD_EXAMPLES OFF CACHE BOOL "")
FetchContent_MakeAvailable(ceres)

add_subdirectory(src/relocal_adr)