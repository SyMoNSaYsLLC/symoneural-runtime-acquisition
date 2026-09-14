# libsymoneural-llm - the SyMoNeuRaL-owned inference ABI over libllama + libggml
# (reconstruction v1.1 §49-§56, L3). Produces libsymoneural-llm.so (+ .a), the public
# header symoneural/llm.h, and symoneural-llm-util. Links the estate's own libllama and
# libggml packages through pkg-config (llama.pc: -lggml -lggml-base -lllama); nothing here
# reaches a build tree or a host toolkit. Built by the recipe symoneural-llm
# (symoneural-firstparty) from the committed tree.
cmake_minimum_required(VERSION 3.20)
project(symoneural-llm VERSION 1.1.1 LANGUAGES C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
add_compile_options(-Wall -Wextra -Werror)
include(GNUInstallDirs)

find_package(PkgConfig REQUIRED)
pkg_check_modules(LLAMA REQUIRED IMPORTED_TARGET llama)
find_package(Threads REQUIRED)

set(SYM_SOURCES native/src/llm.c)
add_library(symoneural-llm SHARED ${SYM_SOURCES})
add_library(symoneural-llm-static STATIC ${SYM_SOURCES})
set_target_properties(symoneural-llm PROPERTIES VERSION ${PROJECT_VERSION} SOVERSION 1 OUTPUT_NAME symoneural-llm)
set_target_properties(symoneural-llm-static PROPERTIES OUTPUT_NAME symoneural-llm)
foreach(t symoneural-llm symoneural-llm-static)
  target_include_directories(${t} PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/native/include> $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)
  target_link_libraries(${t} PRIVATE PkgConfig::LLAMA Threads::Threads ${CMAKE_DL_LIBS})
endforeach()

add_executable(symoneural-llm-util native/src/util-main.c)
target_link_libraries(symoneural-llm-util PRIVATE symoneural-llm)

install(TARGETS symoneural-llm symoneural-llm-static symoneural-llm-util
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})
install(DIRECTORY native/include/symoneural DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
