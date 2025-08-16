cmake_minimum_required(VERSION 3.10)
project(twitter VERSION 1.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add source files
set(SOURCES
    twitter_fast_retrieval.cpp
)

# Add header files
set(HEADERS
    twitter.h
    twitter_fast_retrieval.h
)

add_library(twitter_lib
    ${HEADERS}
    ${SOURCES}
)
# Create executable
add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} twitter_lib)

# ---------------- Google Test ----------------
# Add gtest
add_subdirectory(../third_party/googletest ${CMAKE_BINARY_DIR}/googletest)

enable_testing()

add_executable(tests
    tests/twitter_test.cpp
)
target_link_libraries(tests
    gtest_main
    twitter_lib            # link the code under test
)

include(GoogleTest)
gtest_discover_tests(tests)