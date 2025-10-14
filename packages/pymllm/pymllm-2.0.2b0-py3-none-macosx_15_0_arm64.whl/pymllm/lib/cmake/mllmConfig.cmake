
####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was mllmConfig.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################
include(CMakeFindDependencyMacro)
include(FetchContent)
FetchContent_Declare(
    fmt
    SOURCE_DIR ${CMAKE_CURRENT_LIST_DIR}/../../packages/fmt/
    GIT_TAG 11.2.0
)
FetchContent_MakeAvailable(fmt)
include("${CMAKE_CURRENT_LIST_DIR}/CPM.cmake")
set(STDEXEC_BUILD_EXAMPLES OFF)
CPMAddPackage(
  NAME stdexec
  GITHUB_REPOSITORY NVIDIA/stdexec
  GIT_TAG nvhpc-25.03.rc1
)
include("${CMAKE_CURRENT_LIST_DIR}/MllmTargets.cmake")
set_and_check(MLLM_INCLUDE_DIR "${PACKAGE_PREFIX_DIR}/include")
check_required_components(Mllm)
