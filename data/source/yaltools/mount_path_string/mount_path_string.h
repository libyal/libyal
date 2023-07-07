/*
 * Mount path string functions
 *
 * Copyright (C) ${copyright}, ${tools_authors}
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

#if !defined( _MOUNT_PATH_STRING_H )
#define _MOUNT_PATH_STRING_H

#include <common.h>
#include <types.h>

#include "${tools_name}_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

int mount_path_string_copy_hexadecimal_to_integer_32_bit(
     const system_character_t *string,
     size_t string_size,
     uint32_t *value_32bit,
     libcerror_error_t **error );

int mount_path_string_copy_from_file_entry_path(
     system_character_t **path,
     size_t *path_size,
     const system_character_t *file_entry_path,
     size_t file_entry_path_length,
     libcerror_error_t **error );

int mount_path_string_copy_to_file_entry_path(
     const system_character_t *path,
     size_t path_length,
     system_character_t **file_entry_path,
     size_t *file_entry_path_size,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _MOUNT_PATH_STRING_H ) */

