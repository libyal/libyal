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

#if !defined( _${library_name_upper_case}_INTERNAL_ERROR_H )
#define _${library_name_upper_case}_INTERNAL_ERROR_H

#include <common.h>
#include <file_stream.h>
#include <types.h>

#if !defined( HAVE_LOCAL_${library_name_upper_case} )
#include <${library_name}/error.h>
#endif

#include "${library_name}_extern.h"

#if defined( __cplusplus )
extern "C" {
#endif

#if !defined( HAVE_LOCAL_${library_name_upper_case} )

${library_name_upper_case}_EXTERN \
void ${library_name}_error_free(
      ${library_name}_error_t **error );

${library_name_upper_case}_EXTERN \
int ${library_name}_error_fprint(
     ${library_name}_error_t *error,
     FILE *stream );

${library_name_upper_case}_EXTERN \
int ${library_name}_error_sprint(
     ${library_name}_error_t *error,
     char *string,
     size_t size );

${library_name_upper_case}_EXTERN \
int ${library_name}_error_backtrace_fprint(
     ${library_name}_error_t *error,
     FILE *stream );

${library_name_upper_case}_EXTERN \
int ${library_name}_error_backtrace_sprint(
     ${library_name}_error_t *error,
     char *string,
     size_t size );

#endif /* !defined( HAVE_LOCAL_${library_name_upper_case} ) */

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_upper_case}_INTERNAL_ERROR_H ) */

