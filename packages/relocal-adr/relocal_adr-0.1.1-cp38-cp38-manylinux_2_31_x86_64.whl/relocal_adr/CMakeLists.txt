# set(CMAKE_CXX_STANDARD_REQUIRED ON)
# set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 17)
set(PYBIND11_FINDPYTHON ON)
SET(CMAKE_BUILD_TYPE "Release")

## System dependencies are found with CMake's conventions
find_package(PCL REQUIRED)
find_package(TBB REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# set(CMAKE_AUTOMOC ON)
# set(CMAKE_AUTOUIC ON)
# set(CMAKE_AUTORCC ON)
# set(CMAKE_INCLUDE_CURRENT_DIR ON)

include_directories(
  ${catkin_INCLUDE_DIRS}
  ${PCL_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
  demo
)

pybind11_add_module(${SKBUILD_PROJECT_NAME} cpp/bindings.cpp cpp/adr.cpp)
target_include_directories(${SKBUILD_PROJECT_NAME} PRIVATE 
    ${CMAKE_CURRENT_LIST_DIR}/cpp
    ${PCL_INCLUDE_DIRS}
)
target_link_libraries(${SKBUILD_PROJECT_NAME} PRIVATE 
    ${PCL_LIBRARIES}
    ceres
    TBB::tbb
)
target_compile_definitions(${SKBUILD_PROJECT_NAME} PRIVATE 
  PROJ_NAME=${SKBUILD_PROJECT_NAME})
install(TARGETS ${SKBUILD_PROJECT_NAME} LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME})
