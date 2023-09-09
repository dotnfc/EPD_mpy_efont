#
# The CMake configuration for this module, refer:
# https://docs.micropython.org/en/latest/develop/cmodules.html#structure-of-an-external-c-module
#

# Create an INTERFACE library for our C module.
add_library(usermod_efont INTERFACE)

# message(STATUS "CMAKE_CURRENT_LIST_DIR=> ${CMAKE_CURRENT_LIST_DIR}")

file(GLOB_RECURSE FREETYPEE_SRC ${CMAKE_CURRENT_LIST_DIR}/*.c)

# Add our source files to the lib
target_sources(usermod_efont INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/modefont.c
    ${CMAKE_CURRENT_LIST_DIR}/ff2_mpy.cpp
    ${CMAKE_CURRENT_LIST_DIR}/ff2_mpy_system.c
    ${CMAKE_CURRENT_LIST_DIR}/image_mpy.c
    ${CMAKE_CURRENT_LIST_DIR}/tjpgd/tjpgd.c
    ${CMAKE_CURRENT_LIST_DIR}/pngle/miniz.c
    ${CMAKE_CURRENT_LIST_DIR}/pngle/pngle.c
    ${FREETYPEE_SRC}
)

# Add the current directory as an include directory.
target_include_directories(usermod_efont INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
    ${CMAKE_CURRENT_LIST_DIR}/freetype
    ${CMAKE_CURRENT_LIST_DIR}/tjpgd
    ${CMAKE_CURRENT_LIST_DIR}/pngle
)

target_compile_definitions(usermod_efont INTERFACE)

# Link our INTERFACE library to the usermod target.
target_link_libraries(usermod INTERFACE usermod_efont)

