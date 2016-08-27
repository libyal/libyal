/*
 * Notification functions
 *
 * Copyright (C) ${copyright}, ${authors}
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

#if !defined( _${library_name_upper_case}_NOTIFY_H )
#define _${library_name_upper_case}_NOTIFY_H

#include <common.h>
#include <file_stream.h>
#include <types.h>

#include "${library_name}_extern.h"
#include "${library_name}_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

#if !defined( HAVE_LOCAL_${library_name_upper_case} )

${library_name_upper_case}_EXTERN \
void ${library_name}_notify_set_verbose(
      int verbose );

${library_name_upper_case}_EXTERN \
int ${library_name}_notify_set_stream(
     FILE *stream,
     libcerror_error_t **error );

${library_name_upper_case}_EXTERN \
int ${library_name}_notify_stream_open(
     const char *filename,
     libcerror_error_t **error );

${library_name_upper_case}_EXTERN \
int ${library_name}_notify_stream_close(
     libcerror_error_t **error );

#endif /* !defined( HAVE_LOCAL_${library_name_upper_case} ) */

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_upper_case}_NOTIFY_H ) */

