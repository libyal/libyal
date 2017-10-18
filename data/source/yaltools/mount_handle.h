/*
 * Mount handle
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

#if !defined( _MOUNT_HANDLE_H )
#define _MOUNT_HANDLE_H

#include <common.h>
#include <file_stream.h>
#include <types.h>

#include "${tools_name}_libcdata.h"
#include "${tools_name}_libcerror.h"
#include "${tools_name}_libcnotify.h"
#include "${tools_name}_${library_name}.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct mount_handle mount_handle_t;

struct mount_handle
{
	/* The basename
	 */
	system_character_t *basename;

	/* The basename size
	 */
	size_t basename_size;

	/* The input files array
	 */
	libcdata_array_t *input_files_array;

	/* The key data
	 */
	uint8_t key_data[ 16 ];

	/* Value to indicate the key data is set
	 */
	uint8_t key_data_is_set;

	/* The password
	 */
	const system_character_t *password;

	/* The password length
	 */
	size_t password_length;

	/* The notification output stream
	 */
	FILE *notify_stream;
};

int mount_handle_initialize(
     mount_handle_t **mount_handle,
     libcerror_error_t **error );

int mount_handle_free(
     mount_handle_t **mount_handle,
     libcerror_error_t **error );

int mount_handle_signal_abort(
     mount_handle_t *mount_handle,
     libcerror_error_t **error );

int mount_handle_set_keys(
     mount_handle_t *mount_handle,
     const system_character_t *string,
     libcerror_error_t **error );

int mount_handle_set_password(
     mount_handle_t *mount_handle,
     const system_character_t *string,
     libcerror_error_t **error );

int mount_handle_open_input(
     mount_handle_t *mount_handle,
     const system_character_t *filename,
     libcerror_error_t **error );

int mount_handle_close(
     mount_handle_t *mount_handle,
     libcerror_error_t **error );

ssize_t mount_handle_read_buffer(
         mount_handle_t *mount_handle,
         int input_file_index,
         uint8_t *buffer,
         size_t size,
         libcerror_error_t **error );

off64_t mount_handle_seek_offset(
         mount_handle_t *mount_handle,
         int input_file_index,
         off64_t offset,
         int whence,
         libcerror_error_t **error );

int mount_handle_get_media_size(
     mount_handle_t *mount_handle,
     int input_file_index,
     size64_t *size,
     libcerror_error_t **error );

int mount_handle_get_number_of_input_files(
     mount_handle_t *mount_handle,
     int *number_of_input_files,
     libcerror_error_t **error );

int mount_handle_set_basename(
     mount_handle_t *mount_handle,
     const system_character_t *basename,
     size_t basename_size,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _MOUNT_HANDLE_H ) */

