/*
 * Type definitions for ${library_name}
 *
 * Copyright (C) ${copyright}, ${authors}
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#if !defined( _${library_name:upper_case}_TYPES_H )
#define _${library_name:upper_case}_TYPES_H

#include <${library_name}/features.h>

/* Integer type definitions
 */
#if ( defined( _MSC_VER ) && ( _MSC_VER < 1600 ) ) || ( defined( __BORLANDC__ ) && ( __BORLANDC__ <= 0x0560 ) )

#ifdef __cplusplus
extern "C" {
#endif

/* Microsoft Visual Studio C++ before Visual Studio 2010 or earlier versions of the Borland C++ Builder
 * do not support the (u)int#_t type definitions but have __int# definitions instead
 */
#if !defined( HAVE_INT8_T )
#define HAVE_INT8_T
typedef __int8 int8_t;
#endif

#if !defined( HAVE_UINT8_T )
#define HAVE_UINT8_T
typedef unsigned __int8 uint8_t;
#endif

#if !defined( HAVE_INT16_T )
#define HAVE_INT16_T
typedef __int16 int16_t;
#endif

#if !defined( HAVE_UINT16_T )
#define HAVE_UINT16_T
typedef unsigned __int16 uint16_t;
#endif

#if !defined( HAVE_INT32_T )
#define HAVE_INT32_T
typedef __int32 int32_t;
#endif

#if !defined( HAVE_UINT32_T )
#define HAVE_UINT32_T
typedef unsigned __int32 uint32_t;
#endif

#if !defined( HAVE_INT64_T )
#define HAVE_INT64_T
typedef __int64 int64_t;
#endif

#if !defined( HAVE_UINT64_T )
#define HAVE_UINT64_T
typedef unsigned __int64 uint64_t;
#endif

#ifdef __cplusplus
}
#endif

#elif defined( _MSC_VER ) || defined( __BORLANDC__ )

/* Later versions of Microsoft Visual Studio C++ and Borland C/C++ define the types in <stdint.h>
 */
#include <stdint.h>

#else

#if @HAVE_SYS_TYPES_H@ || defined( HAVE_SYS_TYPES_H )
#include <sys/types.h>

#else
#error Missing system type definitions (sys/types.h)
#endif

/* Type definitions for compilers that have access to
 * <inttypes.h> or <stdint.h>
 */
#if @HAVE_INTTYPES_H@ || defined( HAVE_INTTYPES_H )
#include <inttypes.h>

#elif @HAVE_STDINT_H@ || defined( HAVE_STDINT_H )
#include <stdint.h>

#else
#error Missing integer type definitions (inttypes.h, stdint.h)
#endif

#endif

#ifdef __cplusplus
extern "C" {
#endif

#if defined( _MSC_VER ) || ( defined( __BORLANDC__ ) && ( __BORLANDC__ <= 0x0560 ) )

/* Microsoft Visual Studio C++ or earlier versions of the Borland C++ Builder
 * do not support the ssize_t type definition
 */
#if !defined( HAVE_SSIZE_T )
#define HAVE_SSIZE_T

#if defined( _WIN64 )
typedef __int64 ssize_t;
#else
typedef __int32 ssize_t;
#endif

#endif /* !defined( HAVE_SSIZE_T ) */

#endif /* defined( _MSC_VER ) || ( defined( __BORLANDC__ ) && ( __BORLANDC__ <= 0x0560 ) ) */

#if defined( __BORLANDC__ ) && ( __BORLANDC__ <= 0x0560 )

/* Earlier versions of Borland C++ Builder do not support the intptr_t type definition
 */
#if !defined( HAVE_INTPTR_T )
#define HAVE_INTPTR_T

#if defined( _WIN64 )
typedef __int64	intptr_t;
#else
typedef __int32	intptr_t;
#endif

#endif /* !defined( HAVE_INTPTR_T ) */

#endif /* defined( __BORLANDC__ ) && ( __BORLANDC__ <= 0x0560 ) */

#if ( !defined( HAVE_SIZE32_T ) && ! @HAVE_SIZE32_T@ ) || HAVE_SIZE32_T == 0
#define HAVE_SIZE32_T	1
typedef uint32_t size32_t;
#endif

#if ( !defined( HAVE_SSIZE32_T ) && ! @HAVE_SSIZE32_T@ ) || HAVE_SSIZE32_T == 0
#define HAVE_SSIZE32_T	1
typedef int32_t ssize32_t;
#endif

#if ( !defined( HAVE_SIZE64_T ) && ! @HAVE_SIZE64_T@ ) || HAVE_SIZE64_T == 0
#define HAVE_SIZE64_T	1
typedef uint64_t size64_t;
#endif

#if ( !defined( HAVE_SSIZE64_T ) && ! @HAVE_SSIZE64_T@ ) || HAVE_SSIZE64_T == 0
#define HAVE_SSIZE64_T	1
typedef int64_t ssize64_t;
#endif

#if ( !defined( HAVE_OFF64_T ) && ! @HAVE_OFF64_T@ ) || HAVE_OFF64_T == 0
#define HAVE_OFF64_T	1
typedef int64_t off64_t;
#endif

/* Wide character definition
 */
#if defined( __BORLANDC__ ) && ( __BORLANDC__ <= 0x0520 )
#include <string.h>

#elif defined( WINAPI )
#include <wchar.h>

#elif @HAVE_WCHAR_H@ || defined( HAVE_WCHAR_H )

/* __USE_UNIX98 is required to add swprintf definition
 */
#if !defined( __USE_UNIX98 )
#define __USE_UNIX98
#define ${library_name:upper_case}_DEFINITION_UNIX98
#endif

#include <wchar.h>

#if defined( ${library_name:upper_case}_DEFINITION_UNIX98 )
#undef __USE_UNIX98
#undef ${library_name:upper_case}_DEFINITION_UNIX98
#endif

#endif

