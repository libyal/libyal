/*
 * Library ${library_type} type testing program
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
#include <file_stream.h>

#if defined( HAVE_STDLIB_H ) || defined( WINAPI )
#include <stdlib.h>
#endif

#include "${library_name_suffix}_test_libcerror.h"
#include "${library_name_suffix}_test_libcstring.h"
#include "${library_name_suffix}_test_${library_name}.h"
#include "${library_name_suffix}_test_macros.h"
#include "${library_name_suffix}_test_memory.h"
#include "${library_name_suffix}_test_unused.h"

/* Tests the ${library_name}_${library_type}_initialize function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${library_type}_initialize(
     void )
{
	libcerror_error_t *error             = NULL;
	${library_name}_${library_type}_t *${library_type} = NULL;
	int result                           = 0;

	/* Test ${library_name}_${library_type}_initialize
	 */
	result = ${library_name}_${library_type}_initialize(
	          &${library_type},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
         "${library_type}",
         ${library_type} );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

	result = ${library_name}_${library_type}_free(
	          &${library_type},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "${library_type}",
         ${library_type} );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
         "error",
         error );

	/* Test error cases
	 */
	result = ${library_name}_${library_type}_initialize(
	          NULL,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
         "error",
         error );

	libcerror_error_free(
	 &error );

	${library_type} = (${library_name}_${library_type}_t *) 0x12345678UL;

	result = ${library_name}_${library_type}_initialize(
	          &${library_type},
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
         "error",
         error );

	libcerror_error_free(
	 &error );

	${library_type} = NULL;

#if defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY )

	/* Test ${library_name}_${library_type}_initialize with malloc failing
	 */
	${library_name_suffix}_test_malloc_attempts_before_fail = 0;

	result = ${library_name}_${library_type}_initialize(
	          &${library_type},
	          &error );

	if( ${library_name_suffix}_test_malloc_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_malloc_attempts_before_fail = -1;
	}
	else
	{
		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 -1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "${library_type}",
		 ${library_type} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
	/* Test ${library_name}_${library_type}_initialize with memset failing
	 */
	${library_name_suffix}_test_memset_attempts_before_fail = 0;

	result = ${library_name}_${library_type}_initialize(
	          &${library_type},
	          &error );

	if( ${library_name_suffix}_test_memset_attempts_before_fail != -1 )
	{
		${library_name_suffix}_test_memset_attempts_before_fail = -1;
	}
	else
	{
		${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
		 "result",
		 result,
		 -1 );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NULL(
		 "${library_type}",
		 ${library_type} );

		${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
		 "error",
		 error );

		libcerror_error_free(
		 &error );
	}
#endif /* defined( HAVE_${library_name_suffix_upper_case}_TEST_MEMORY ) */

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	if( ${library_type} != NULL )
	{
		${library_name}_${library_type}_free(
		 &${library_type},
		 NULL );
	}
	return( 0 );
}

/* Tests the ${library_name}_${library_type}_free function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${library_type}_free(
     void )
{
	libcerror_error_t *error = NULL;
	int result               = 0;

	/* Test error cases
	 */
	result = ${library_name}_${library_type}_free(
	          NULL,
	          &error );

	${library_name_suffix_upper_case}_TEST_ASSERT_EQUAL_INT(
	 "result",
	 result,
	 -1 );

        ${library_name_suffix_upper_case}_TEST_ASSERT_IS_NOT_NULL(
         "error",
         error );

	libcerror_error_free(
	 &error );

	return( 1 );

on_error:
	if( error != NULL )
	{
		libcerror_error_free(
		 &error );
	}
	return( 0 );
}

