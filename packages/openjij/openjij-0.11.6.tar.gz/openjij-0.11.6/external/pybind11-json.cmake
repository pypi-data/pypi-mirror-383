include(FetchContent)

message(CHECK_START "Fetching Pybind11 Json")
list(APPEND CMAKE_MESSAGE_INDENT "  ")

set(FETCHCONTENT_QUIET OFF)
#### pybind11_json ####
FetchContent_Declare(
    pybind11_json
    GIT_REPOSITORY  https://github.com/pybind/pybind11_json
    GIT_TAG         0.2.15
    GIT_SHALLOW     TRUE
)
set(BUILD_TESTING OFF)
# Prevent pybind11_json from being installed by using FetchContent_Populate + add_subdirectory with EXCLUDE_FROM_ALL
FetchContent_GetProperties(pybind11_json)
if(NOT pybind11_json_POPULATED)
    FetchContent_Populate(pybind11_json)
    add_subdirectory(${pybind11_json_SOURCE_DIR} ${pybind11_json_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

list(POP_BACK CMAKE_MESSAGE_INDENT)
message(CHECK_PASS "fetched")
