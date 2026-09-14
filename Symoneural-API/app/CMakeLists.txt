# libsymoneural-api - the native half of the SyMoNeuRaL API (reconstruction v1.1 §29-§34).
# Produces libsymoneural-api.so (+ .a), public headers, and symoneural-api-util.
# Depends on libc/POSIX only. Built by the estate recipe symoneural-api (symoneural-firstparty) and,
# for the host regression run, by tests/native/Makefile + this file.
cmake_minimum_required(VERSION 3.20)
project(symoneural-api VERSION 1.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
add_compile_options(-Wall -Wextra -Werror -D_POSIX_C_SOURCE=200809L)
include(GNUInstallDirs)

set(SYM_SOURCES src/gpulock.c src/unit.c src/rack.c src/api.c)
add_library(symoneural-api SHARED ${SYM_SOURCES})
add_library(symoneural-api-static STATIC ${SYM_SOURCES})
set_target_properties(symoneural-api PROPERTIES VERSION ${PROJECT_VERSION} SOVERSION 1 OUTPUT_NAME symoneural-api)
set_target_properties(symoneural-api-static PROPERTIES OUTPUT_NAME symoneural-api)
foreach(t symoneural-api symoneural-api-static)
  target_include_directories(${t} PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include> $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)
endforeach()

add_executable(symoneural-api-util src/util-main.c)
target_link_libraries(symoneural-api-util PRIVATE symoneural-api)

install(TARGETS symoneural-api symoneural-api-static symoneural-api-util
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(DIRECTORY include/symoneural DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

enable_testing()
foreach(t gpulock unit rack api)
  add_executable(test_${t} tests/native/test_${t}.c)
  target_link_libraries(test_${t} PRIVATE symoneural-api-static)
  target_include_directories(test_${t} PRIVATE tests/native)
  add_test(NAME ${t} COMMAND test_${t})
endforeach()
