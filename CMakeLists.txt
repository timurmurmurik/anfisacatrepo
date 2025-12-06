cmake_minimum_required(VERSION 3.16)
project(ElysiumArchitect LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(elysium
    src/materials/materials.cpp
    src/world/world.cpp
    src/physics/physics.cpp
    src/simulation/simulation.cpp
)

target_include_directories(elysium PUBLIC src)

enable_testing()
add_executable(engine_tests tests/test_engine.cpp)
target_link_libraries(engine_tests PRIVATE elysium)
add_test(NAME engine_tests COMMAND engine_tests)
