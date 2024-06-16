/*
 * Memory allocation functions for testing
 *
 * Copyright (C) ${copyright}, ${tests_authors}
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

#if !defined( _${library_name_suffix:upper_case}_TEST_MEMORY_H )
#define _${library_name_suffix:upper_case}_TEST_MEMORY_H

#include <common.h>

#if defined( __cplusplus )
extern "C" {
#endif

#if defined( HAVE_GNU_DL_DLSYM ) && defined( __GNUC__ ) && !defined( ${library_name:upper_case}_DLL_IMPORT ) && !defined( __arm__ ) && !defined( __clang__ ) && !defined( __CYGWIN__ ) && !defined( __hppa__ ) && !defined( __loongarch__ ) && !defined( __mips__ ) && !defined( __riscv ) && !defined( __sparc__ ) && !defined( HAVE_ASAN )
#define HAVE_${library_name_suffix:upper_case}_TEST_MEMORY		1
#endif

#if defined( HAVE_${library_name_suffix:upper_case}_TEST_MEMORY )

extern int ${library_name_suffix}_test_malloc_attempts_before_fail;

extern int ${library_name_suffix}_test_memcpy_attempts_before_fail;

extern int ${library_name_suffix}_test_memset_attempts_before_fail;

extern int ${library_name_suffix}_test_realloc_attempts_before_fail;

#endif /* defined( HAVE_${library_name_suffix:upper_case}_TEST_MEMORY ) */

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_suffix:upper_case}_TEST_MEMORY_H ) */

