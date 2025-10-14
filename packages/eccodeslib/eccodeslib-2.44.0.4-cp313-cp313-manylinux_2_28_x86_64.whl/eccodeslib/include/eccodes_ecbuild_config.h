/*
 * (C) Copyright 2011- ECMWF.
 *
 * This software is licensed under the terms of the Apache Licence Version 2.0
 * which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
 * In applying this licence, ECMWF does not waive the privileges and immunities
 * granted to it by virtue of its status as an intergovernmental organisation nor
 * does it submit to any jurisdiction.
 */

#ifndef ECCODES_ecbuild_config_h
#define ECCODES_ecbuild_config_h

/* ecbuild info */

#ifndef ECBUILD_VERSION_STR
#define ECBUILD_VERSION_STR "3.12.0"
#endif
#ifndef ECBUILD_VERSION
#define ECBUILD_VERSION "3.12.0"
#endif
#ifndef ECBUILD_MACROS_DIR
#define ECBUILD_MACROS_DIR  "/src/ecbuild/cmake"
#endif

/* config info */

#define ECCODES_OS_NAME          "Linux-4.18.0-372.26.1.el8_6.x86_64"
#define ECCODES_OS_BITS          64
#define ECCODES_OS_BITS_STR      "64"
#define ECCODES_OS_STR           "linux.64"
#define ECCODES_OS_VERSION       "4.18.0-372.26.1.el8_6.x86_64"
#define ECCODES_SYS_PROCESSOR    "x86_64"

#define ECCODES_BUILD_TIMESTAMP  "20251013104152"
#define ECCODES_BUILD_TYPE       "RelWithDebInfo"

#define ECCODES_C_COMPILER_ID      "GNU"
#define ECCODES_C_COMPILER_VERSION "13.3.1"

#define ECCODES_CXX_COMPILER_ID      "GNU"
#define ECCODES_CXX_COMPILER_VERSION "13.3.1"

#define ECCODES_C_COMPILER       "/opt/rh/gcc-toolset-13/root/usr/bin/cc"
#define ECCODES_C_FLAGS          " -pipe -O2 -g -DNDEBUG"

#define ECCODES_CXX_COMPILER     "/opt/rh/gcc-toolset-13/root/usr/bin/c++"
#define ECCODES_CXX_FLAGS        " -pipe -O2 -g -DNDEBUG"

/* Needed for finding per package config files */

#define ECCODES_INSTALL_DIR       "/tmp/eccodes/target/eccodes"
#define ECCODES_INSTALL_BIN_DIR   "/tmp/eccodes/target/eccodes/bin"
#define ECCODES_INSTALL_LIB_DIR   "/tmp/eccodes/target/eccodes/lib64"
#define ECCODES_INSTALL_DATA_DIR  "/tmp/eccodes/target/eccodes/share/eccodes"

#define ECCODES_DEVELOPER_SRC_DIR "/src/eccodes"
#define ECCODES_DEVELOPER_BIN_DIR "/tmp/eccodes/build"

/* Fortran support */

#if 1

#define ECCODES_Fortran_COMPILER_ID      "IntelLLVM"
#define ECCODES_Fortran_COMPILER_VERSION "2025.2.1"

#define ECCODES_Fortran_COMPILER "/opt/intel/oneapi/compiler/latest/bin/ifx"
#define ECCODES_Fortran_FLAGS    " -O2 -g"

#endif

#endif /* ECCODES_ecbuild_config_h */
