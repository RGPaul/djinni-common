cmake_minimum_required (VERSION 3.6)

project(djinni-common)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if (NOT (DJINNI_WITH_OBJC OR DJINNI_WITH_JNI))
  message(FATAL_ERROR "At least one of DJINNI_WITH_OBJC or DJINNI_WITH_JNI must be enabled.")
endif()

# Conan installs Library Config Files to the CMAKE_BINARY_DIR
set(CMAKE_PREFIX_PATH ${CMAKE_PREFIX_PATH} ${CMAKE_BINARY_DIR})
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR})

# ----------------------------------------------------------------------------------------------------------------------
# General
# ----------------------------------------------------------------------------------------------------------------------

set(CMAKE_INCLUDE_CURRENT_DIR ON)

# djinni generated code for objc
file(GLOB objc_generated_src "${CMAKE_CURRENT_LIST_DIR}/generated-src/objc/*.mm")
file(GLOB objc_generated_headers "${CMAKE_CURRENT_LIST_DIR}/generated-src/objc/*.h")
file(GLOB objcpp_generated_src "${CMAKE_CURRENT_LIST_DIR}/generated-src/objcpp/*.mm")
file(GLOB objcpp_generated_headers "${CMAKE_CURRENT_LIST_DIR}/generated-src/objcpp/*.h")
# djinni generated code jni
file(GLOB jni_generated_src "${CMAKE_CURRENT_LIST_DIR}/generated-src/jni/*.cpp")
file(GLOB jni_generated_headers "${CMAKE_CURRENT_LIST_DIR}/generated-src/jni/*.hpp")
# djinni generated code c++
file(GLOB cpp_generated_headers "${CMAKE_CURRENT_LIST_DIR}/generated-src/cpp/*.hpp")

# implementation
file(GLOB cpp_src "${CMAKE_CURRENT_LIST_DIR}/src/cpp/*.cpp")
file(GLOB cpp_headers "${CMAKE_CURRENT_LIST_DIR}/src/cpp/*.hpp")
file(GLOB objc_src "${CMAKE_CURRENT_LIST_DIR}/src/objc/*.m")
file(GLOB objc_headers "${CMAKE_CURRENT_LIST_DIR}/src/objc/*.h")

# ----------------------------------------------------------------------------------------------------------------------
# Boost - http://www.boost.org
# ----------------------------------------------------------------------------------------------------------------------

add_definitions(-DBOOST_FILESYSTEM_NO_DEPRECATED)
find_package(Boost 1.82.0 REQUIRED)

# ----------------------------------------------------------------------------------------------------------------------
# NLohmann-JSON: https://github.com/nlohmann/json
# ----------------------------------------------------------------------------------------------------------------------
find_package(nlohmann_json REQUIRED)

# ----------------------------------------------------------------------------------------------------------------------
# Dropbox djinni support library - https://github.com/dropbox/djinni
# ----------------------------------------------------------------------------------------------------------------------

find_package(djinni REQUIRED)

# ----------------------------------------------------------------------------------------------------------------------
# djinni-common
# ----------------------------------------------------------------------------------------------------------------------

option(BUILD_STATIC_LIB "Build appcom-djinni-common library as a static library instead of dynamic (the default)." OFF)
if(BUILD_STATIC_LIB)
  add_library(appcom-djinni-common STATIC ${cpp_src})
else()
  add_library(appcom-djinni-common SHARED ${cpp_src})
endif()
source_group("" FILES ${cpp_src})

# Objective-C support
option(DJINNI_WITH_OBJC "Include the Objective-C support code in appcom-djinni-common library." OFF)
if(DJINNI_WITH_OBJC)
  target_sources(appcom-djinni-common PRIVATE ${objc_generated_src} ${objcpp_generated_src} ${objc_src})
  source_group("objc" FILES ${objc_generated_src} ${objcpp_generated_src} ${objc_src})
  set_target_properties(appcom-djinni-common PROPERTIES COMPILE_FLAGS "-fobjc-arc")
  target_include_directories(appcom-djinni-common PRIVATE
                            # djinni support library
                            "${djinni_INCLUDE_DIR}/djinni/"
                            "${djinni_INCLUDE_DIR}/djinni/objc"
                            # djinni generated
                            "${CMAKE_CURRENT_LIST_DIR}/generated-src/objc"
                            "${CMAKE_CURRENT_LIST_DIR}/generated-src/objcpp"
                            "${CMAKE_CURRENT_LIST_DIR}/generated-src/cpp"
                            # implementation
                            "${CMAKE_CURRENT_LIST_DIR}/src/cpp"
                            "${CMAKE_CURRENT_LIST_DIR}/src/objc")
endif()

# JNI support
option(DJINNI_WITH_JNI "Include the JNI support code in appcom-djinni-common library." OFF)
if(DJINNI_WITH_JNI)
  target_sources(appcom-djinni-common PRIVATE ${jni_support_src} ${jni_generated_src})
  source_group("jni" FILES ${jni_support_src} ${jni_generated_src})
  target_include_directories(appcom-djinni-common PRIVATE
                            # djinni support library
                            "${djinni_INCLUDE_DIR}/djinni/"
                            "${djinni_INCLUDE_DIR}/djinni/jni"
                            # djinni generated
                            "${CMAKE_CURRENT_LIST_DIR}/generated-src/jni"
                            "${CMAKE_CURRENT_LIST_DIR}/generated-src/cpp"
                            # implementation
                            "${CMAKE_CURRENT_LIST_DIR}/src")

  # Do not use the host's jni.h on Android as it is provided automatically by the NDK
  if(NOT ANDROID)
    find_package(JNI REQUIRED QUIET)
    target_include_directories(appcom-djinni-common PUBLIC "${JNI_INCLUDE_DIRS}")
  else()
    # for android we have to link some android libraries
    target_link_libraries(appcom-djinni-common android log)
  endif()
endif()

target_link_libraries(appcom-djinni-common boost::boost nlohmann_json::nlohmann_json djinni::djinni)

install(TARGETS appcom-djinni-common
        LIBRARY DESTINATION "lib"
        ARCHIVE DESTINATION "lib")

if(DJINNI_WITH_OBJC)
  install(FILES 
          ${objc_generated_headers} 
          ${cpp_headers} 
          ${objc_headers} 
          ${objcpp_generated_headers} 
          ${cpp_generated_headers}
          DESTINATION "include/appcom/djinni/common")
endif()

if(DJINNI_WITH_JNI)

  install(DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/generated-src/java/eu"
          DESTINATION "jni")

  install(DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/src/android/eu" 
          DESTINATION "jni")

  install(DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/src/java/eu"
          DESTINATION "jni")

  install(FILES ${jni_generated_headers} ${cpp_generated_headers} ${cpp_headers}
          DESTINATION "include/appcom/djinni/common")
endif()

install(FILES "appcom-common.yml"
        DESTINATION ".")
