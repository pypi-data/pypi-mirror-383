include(FetchContent)

message(CHECK_START "Fetching JSON")
list(APPEND CMAKE_MESSAGE_INDENT "  ")

set(BUILD_TESTING OFF)

# Set policy version minimum to fix compatibility issue with CMake 4.0.0
set(CMAKE_POLICY_VERSION_MINIMUM 3.5 CACHE STRING "Minimum CMake policy version" FORCE)

#### nlohmann_json ####
FetchContent_Declare(
     nlohmann_json
     GIT_REPOSITORY  https://github.com/nlohmann/json
     GIT_TAG         v3.12.0
     GIT_SHALLOW     TRUE
     )
     
# Prevent nlohmann_json from being installed by using FetchContent_Populate + add_subdirectory with EXCLUDE_FROM_ALL
FetchContent_GetProperties(nlohmann_json)
if(NOT nlohmann_json_POPULATED)
    FetchContent_Populate(nlohmann_json)
    add_subdirectory(${nlohmann_json_SOURCE_DIR} ${nlohmann_json_BINARY_DIR} EXCLUDE_FROM_ALL)
endif()

# Since the git repository of nlohmann/json is huge, we store only a single-include file json.hpp in our project.
#set(BUILD_TESTING OFF)
#add_library(nlohmann_json INTERFACE)
#add_library(nlohmann_json::nlohmann_json ALIAS nlohmann_json)
#target_include_directories(nlohmann_json INTERFACE ${CMAKE_SOURCE_DIR}/external/nlohmann_json)

list(POP_BACK CMAKE_MESSAGE_INDENT)
message(CHECK_PASS "fetched")
