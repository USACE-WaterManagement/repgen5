project(repgen5)

add_executable(repgen5 program.cpp mildatetime.cpp repgenutil.cpp value.cpp report.cpp options.cpp main.cpp)


add_subdirectory(test)