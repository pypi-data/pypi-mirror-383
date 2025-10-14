#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mllm::MllmCPUBackend" for configuration "Release"
set_property(TARGET mllm::MllmCPUBackend APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mllm::MllmCPUBackend PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libMllmCPUBackend.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libMllmCPUBackend.dylib"
  )

list(APPEND _cmake_import_check_targets mllm::MllmCPUBackend )
list(APPEND _cmake_import_check_files_for_mllm::MllmCPUBackend "${_IMPORT_PREFIX}/lib/libMllmCPUBackend.dylib" )

# Import target "mllm::MllmFFIExtension" for configuration "Release"
set_property(TARGET mllm::MllmFFIExtension APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mllm::MllmFFIExtension PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/MllmFFIExtension.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/MllmFFIExtension.dylib"
  )

list(APPEND _cmake_import_check_targets mllm::MllmFFIExtension )
list(APPEND _cmake_import_check_files_for_mllm::MllmFFIExtension "${_IMPORT_PREFIX}/lib/MllmFFIExtension.dylib" )

# Import target "mllm::tvm_ffi_shared" for configuration "Release"
set_property(TARGET mllm::tvm_ffi_shared APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mllm::tvm_ffi_shared PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libtvm_ffi.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libtvm_ffi.dylib"
  )

list(APPEND _cmake_import_check_targets mllm::tvm_ffi_shared )
list(APPEND _cmake_import_check_files_for_mllm::tvm_ffi_shared "${_IMPORT_PREFIX}/lib/libtvm_ffi.dylib" )

# Import target "mllm::MllmRT" for configuration "Release"
set_property(TARGET mllm::MllmRT APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mllm::MllmRT PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libMllmRT.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libMllmRT.dylib"
  )

list(APPEND _cmake_import_check_targets mllm::MllmRT )
list(APPEND _cmake_import_check_files_for_mllm::MllmRT "${_IMPORT_PREFIX}/lib/libMllmRT.dylib" )

# Import target "mllm::xxhash_static" for configuration "Release"
set_property(TARGET mllm::xxhash_static APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mllm::xxhash_static PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "C"
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libxxhash_static.a"
  )

list(APPEND _cmake_import_check_targets mllm::xxhash_static )
list(APPEND _cmake_import_check_files_for_mllm::xxhash_static "${_IMPORT_PREFIX}/lib/libxxhash_static.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
