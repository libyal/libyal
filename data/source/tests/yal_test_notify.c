/*
 * Library notification functions test program
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

#include "${library_name_suffix}_test_libcerror.h"
#include "${library_name_suffix}_test_${library_name}.h"
#include "${library_name_suffix}_test_macros.h"
#include "${library_name_suffix}_test_unused.h"

/* Tests the ${library_name}_notify_set_verbose function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_notify_set_verbose(
     void )
{
	/* Test invocation of function only
	 */
	${library_name}_notify_set_verbose(
	 0 );

	return( 1 );
}

/* Tests the ${library_name}_notify_set_stream function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_notify_set_stream(
     void )
{
	/* Test invocation of function only
	 */
	${library_name}_notify_set_stream(
	 NULL,
	 NULL );

	return( 1 );
}

/* Tests the ${library_name}_notify_stream_open function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_notify_stream_open(
     void )
{
	/* Test invocation of function only
	 */
	${library_name}_notify_stream_open(
	 NULL,
	 NULL );

	return( 1 );
}

/* Tests the ${library_name}_notify_stream_close function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_notify_stream_close(
     void )
{
	/* Test invocation of function only
	 */
	${library_name}_notify_stream_close(
	 NULL );

	return( 1 );
}

/* The main program
 */
#if defined( LIBCSTRING_HAVE_WIDE_SYSTEM_CHARACTER )
int wmain(
     int argc ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED,
     wchar_t * const argv[] ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED )
#else
int main(
     int argc ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED,
     char * const argv[] ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED )
#endif
{
	${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( argc )
	${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( argv )

	${library_name_suffix_upper_case}_TEST_RUN(
	 "${library_name}_notify_set_verbose",
	 ${library_name_suffix}_test_notify_set_verbose() )

	${library_name_suffix_upper_case}_TEST_RUN(
	 "${library_name}_notify_set_stream",
	 ${library_name_suffix}_test_notify_set_stream() )

	${library_name_suffix_upper_case}_TEST_RUN(
	 "${library_name}_notify_stream_open",
	 ${library_name_suffix}_test_notify_stream_open() )

	${library_name_suffix_upper_case}_TEST_RUN(
	 "${library_name}_notify_stream_close",
	 ${library_name_suffix}_test_notify_stream_close() )

	return( EXIT_SUCCESS );

on_error:
	return( EXIT_FAILURE );
}

