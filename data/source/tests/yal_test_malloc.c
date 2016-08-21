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

#include <common.h>

#if defined( HAVE_STDLIB_H ) || defined( WINAPI )
#include <stdlib.h>
#endif

#if defined( HAVE_GNU_DL_DLSYM ) && !defined( WINAPI )
#define __USE_GNU
#include <dlfcn.h>
#undef __USE_GNU
#endif

#if defined( HAVE_GNU_DL_DLSYM ) && !defined( WINAPI )

static void *(*${library_name_suffix}_test_real_malloc)(size_t)             = NULL;
static void *(*${library_name_suffix}_test_real_realloc)(void *ptr, size_t) = NULL;

int ${library_name_suffix}_test_malloc_attempts_before_fail                 = -1;
int ${library_name_suffix}_test_realloc_attempts_before_fail                = -1;

/* Custom malloc for testing memory error cases
 * Returns a pointer to newly allocated data or NULL
 */
void *malloc(
       size_t size )
{
	if( ${library_name_suffix}_test_real_malloc == NULL )
	{
		${library_name_suffix}_test_real_malloc = dlsym(
		 RTLD_NEXT,
		 "malloc" );
	}
	if( ${library_name_suffix}_test_malloc_attempts_before_fail == 0 )
	{
		return( NULL );
	}
	if( ${library_name_suffix}_test_malloc_attempts_before_fail > 0 )
	{
		${library_name_suffix}_test_malloc_attempts_before_fail--;
	}
	return(
	 ${library_name_suffix}_test_real_malloc(
	  size ) );
}

/* Custom realloc for testing memory error cases
 * Returns a pointer to reallocated data or NULL
 */
void *realloc(
       void *ptr,
       size_t size )
{
	if( ${library_name_suffix}_test_real_realloc == NULL )
	{
		${library_name_suffix}_test_real_realloc = dlsym(
		 RTLD_NEXT,
		 "realloc" );
	}
	if( ${library_name_suffix}_test_realloc_attempts_before_fail == 0 )
	{
		return( NULL );
	}
	if( ${library_name_suffix}_test_realloc_attempts_before_fail > 0 )
	{
		${library_name_suffix}_test_realloc_attempts_before_fail--;
	}
	return(
	 ${library_name_suffix}_test_real_realloc(
	  ptr,
	  size ) );
}

#endif /* defined( HAVE_GNU_DL_DLSYM ) && !defined( WINAPI ) */

