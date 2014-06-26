project(repgen5)

add_executable(repgen5 calculator.cpp mildatetime.cpp repgenutil.cpp value.cpp queue.cpp report.cpp options.cpp main.cpp)


add_subdirectory(test)