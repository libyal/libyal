/*
 * Error functions
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

#include <common.h>
#include <file_stream.h>
#include <types.h>

#include "${library_name}_error.h"
#include "${library_name}_libcerror.h"

#if !defined( HAVE_LOCAL_${library_name:upper_case} )

/* Free an error and its elements
 */
void ${library_name}_error_free(
      ${library_name}_error_t **error )
{
	libcerror_error_free(
	 (libcerror_error_t **) error );
}

/* Prints a descriptive string of the error to the stream
 * Returns the number of printed characters if successful or -1 on error
 */
int ${library_name}_error_fprint(
     ${library_name}_error_t *error,
     FILE *stream )
{
	int print_count = 0;

	print_count = libcerror_error_fprint(
	               (libcerror_error_t *) error,
	               stream );

	return( print_count );
}

/* Prints a descriptive string of the error to the string
 * The end-of-string character is not included in the return value
 * Returns the number of printed characters if successful or -1 on error
 */
int ${library_name}_error_sprint(
     ${library_name}_error_t *error,
     char *string,
     size_t size )
{
	int print_count = 0;

	print_count = libcerror_error_sprint(
	               (libcerror_error_t *) error,
	               string,
	               size );

	return( print_count );
}

/* Prints a backtrace of the error to the stream
 * Returns the number of printed characters if successful or -1 on error
 */
int ${library_name}_error_backtrace_fprint(
     ${library_name}_error_t *error,
      FILE *stream )
{
	int print_count = 0;

	print_count = libcerror_error_backtrace_fprint(
	               (libcerror_error_t *) error,
	               stream );

	return( print_count );
}

/* Prints a backtrace of the error to the string
 * The end-of-string character is not included in the return value
 * Returns the number of printed characters if successful or -1 on error
 */
int ${library_name}_error_backtrace_sprint(
     ${library_name}_error_t *error,
     char *string,
     size_t size )
{
	int print_count = 0;

	print_count = libcerror_error_backtrace_sprint(
	               (libcerror_error_t *) error,
	               string,
	               size );

	return( print_count );
}

#endif /* !defined( HAVE_LOCAL_${library_name:upper_case} ) */

