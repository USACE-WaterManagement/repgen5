cmake_minimum_required(VERSION 3.0)

project(repgen5)

add_executable(repgen5 instruction.cpp program.cpp mildatetime.cpp repgenutil.cpp value.cpp report.cpp options.cpp main.cpp)


add_subdirectory(test)
