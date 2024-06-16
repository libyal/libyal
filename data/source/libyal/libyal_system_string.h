/*
 * System string functions
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

#if !defined( _${library_name:upper_case}_SYSTEM_STRING_H )
#define _${library_name:upper_case}_SYSTEM_STRING_H

#include <common.h>
#include <types.h>

#include "${library_name}_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

int ${library_name}_system_string_size_to_narrow_string(
     const system_character_t *system_string,
     size_t system_string_size,
     size_t *narrow_string_size,
     libcerror_error_t **error );

int ${library_name}_system_string_copy_to_narrow_string(
     const system_character_t *system_string,
     size_t system_string_size,
     char *narrow_string,
     size_t narrow_string_size,
     libcerror_error_t **error );

int ${library_name}_system_string_size_from_narrow_string(
     const char *narrow_string,
     size_t narrow_string_size,
     size_t *system_string_size,
     libcerror_error_t **error );

int ${library_name}_system_string_copy_from_narrow_string(
     system_character_t *system_string,
     size_t system_string_size,
     const char *narrow_string,
     size_t narrow_string_size,
     libcerror_error_t **error );

#if defined( HAVE_WIDE_CHARACTER_TYPE )

int ${library_name}_system_string_size_to_wide_string(
     const system_character_t *system_string,
     size_t system_string_size,
     size_t *wide_string_size,
     libcerror_error_t **error );

int ${library_name}_system_string_copy_to_wide_string(
     const system_character_t *system_string,
     size_t system_string_size,
     wchar_t *wide_string,
     size_t wide_string_size,
     libcerror_error_t **error );

int ${library_name}_system_string_size_from_wide_string(
     const wchar_t *wide_string,
     size_t wide_string_size,
     size_t *system_string_size,
     libcerror_error_t **error );

int ${library_name}_system_string_copy_from_wide_string(
     system_character_t *system_string,
     size_t system_string_size,
     const wchar_t *wide_string,
     size_t wide_string_size,
     libcerror_error_t **error );

#endif /* defined( HAVE_WIDE_CHARACTER_TYPE ) */

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name:upper_case}_SYSTEM_STRING_H ) */

