project( crypt )

cmake_minimum_required(VERSION 2.6)

ADD_DEFINITIONS(
  -std=c++11
  -w
  -lpthread
  -Ofast
  )

find_package(JPEG)

set(EXECUTABLE_OUTPUT_PATH bin/${CMAKE_BUILD_TYPE})

file(

  GLOB_RECURSE

  source_files

  src/*

  )

add_executable(

  crypt

  ${source_files}

  )
include_directories(${JPEG_INCLUDE_DIRS})
target_link_libraries(crypt ${JPEG_LIBRARIES} -lpthread -lX11)
