/*
 * Mount file system
 *
 * Copyright (C) ${copyright}, ${tools_authors}
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

#if !defined( _MOUNT_FILE_SYSTEM_H )
#define _MOUNT_FILE_SYSTEM_H

#include <common.h>
#include <types.h>

#include "${tools_name}_libcdata.h"
#include "${tools_name}_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct mount_file_system mount_file_system_t;

struct mount_file_system
{
	/* The path prefix
	 */
	system_character_t *path_prefix;

	/* The path prefix size
	 */
	size_t path_prefix_size;

	/* The mounted timestamp
	 */
	int64_t mounted_timestamp;

	/* The ${mount_tool_source_type}s array
	 */
	libcdata_array_t *${mount_tool_source_type}s_array;
};

int mount_file_system_initialize(
     mount_file_system_t **file_system,
     libcerror_error_t **error );

int mount_file_system_free(
     mount_file_system_t **file_system,
     libcerror_error_t **error );

int mount_file_system_signal_abort(
     mount_file_system_t *file_system,
     libcerror_error_t **error );

int mount_file_system_set_path_prefix(
     mount_file_system_t *file_system,
     const system_character_t *path_prefix,
     size_t path_prefix_size,
     libcerror_error_t **error );

int mount_file_system_get_mounted_timestamp(
     mount_file_system_t *file_system,
     int64_t *mounted_timestamp,
     libcerror_error_t **error );

int mount_file_system_get_number_of_${mount_tool_source_type}s(
     mount_file_system_t *file_system,
     int *number_of_${mount_tool_source_type}s,
     libcerror_error_t **error );

int mount_file_system_get_${mount_tool_source_type}_by_index(
     mount_file_system_t *file_system,
     int ${mount_tool_source_type}_index,
     ${library_name}_${mount_tool_library_type}_t **${mount_tool_source_type},
     libcerror_error_t **error );

int mount_file_system_append_${mount_tool_source_type}(
     mount_file_system_t *file_system,
     ${library_name}_${mount_tool_library_type}_t *${mount_tool_source_type},
     libcerror_error_t **error );

int mount_file_system_get_${mount_tool_source_type}_index_from_path(
     mount_file_system_t *file_system,
     const system_character_t *path,
     size_t path_length,
     int *${mount_tool_source_type}_index,
     libcerror_error_t **error );

int mount_file_system_get_path_from_${mount_tool_source_type}_index(
     mount_file_system_t *file_system,
     int ${mount_tool_source_type}_index,
     system_character_t *path,
     size_t path_size,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _MOUNT_FILE_SYSTEM_H ) */

