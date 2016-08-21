/*
 * Memory allocation functions for testing
 *
 * Copyright (C) ${copyright}, ${tests_authors}
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This software is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this software.  If not, see <http://www.gnu.org/licenses/>.
 */

#if !defined( _${library_name_suffix_upper_case}_TEST_MALLOC_H )
#define _${library_name_suffix_upper_case}_TEST_MALLOC_H

#include <common.h>

#if defined( __cplusplus )
extern "C" {
#endif

#if defined( HAVE_GNU_DL_DLSYM ) && !defined( WINAPI )

#define HAVE_${library_name_suffix_upper_case}_TEST_MALLOC		1

extern int ${library_name_suffix}_test_malloc_attempts_before_fail;

extern int ${library_name_suffix}_test_realloc_attempts_before_fail;

#endif /* defined( HAVE_GNU_DL_DLSYM ) && !defined( WINAPI ) */

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_suffix_upper_case}_TEST_MALLOC_H ) */

