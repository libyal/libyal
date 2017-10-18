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

#include <common.h>
#include <memory.h>
#include <narrow_string.h>
#include <system_string.h>
#include <types.h>
#include <wide_string.h>

#include "mount_handle.h"
#include "${tools_name}_libcpath.h"
#include "${tools_name}_libcerror.h"
#include "${tools_name}_libcnotify.h"
#include "${tools_name}_libcpath.h"
#include "${tools_name}_${library_name}.h"
#include "${tools_name}_libuna.h"

/* Creates a mount handle
 * Make sure the value mount_handle is referencing, is set to NULL
 * Returns 1 if successful or -1 on error
 */
int mount_handle_initialize(
     mount_handle_t **mount_handle,
     libcerror_error_t **error )
{
	static char *function = "mount_handle_initialize";

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( *mount_handle != NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_ALREADY_SET,
		 "%s: invalid mount handle value already set.",
		 function );

		return( -1 );
	}
	*mount_handle = memory_allocate_structure(
	                 mount_handle_t );

	if( *mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create mount handle.",
		 function );

		goto on_error;
	}
	if( memory_set(
	     *mount_handle,
	     0,
	     sizeof( mount_handle_t ) ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear mount handle.",
		 function );

		goto on_error;
	}
	if( libcdata_array_initialize(
	     &( ( *mount_handle )->input_files_array ),
	     0,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize input files array.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( *mount_handle != NULL )
	{
		memory_free(
		 *mount_handle );

		*mount_handle = NULL;
	}
	return( -1 );
}

/* Frees a mount handle
 * Returns 1 if successful or -1 on error
 */
int mount_handle_free(
     mount_handle_t **mount_handle,
     libcerror_error_t **error )
{
	static char *function = "mount_handle_free";
	int result            = 1;

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( *mount_handle != NULL )
	{
		if( ( *mount_handle )->basename != NULL )
		{
			memory_free(
			 ( *mount_handle )->basename );
		}
		if( libcdata_array_free(
		     &( ( *mount_handle )->input_files_array ),
		     (int (*)(intptr_t **, libcerror_error_t **)) &${library_name}_file_free,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free input files array.",
			 function );

			result = -1;
		}
		if( memory_set(
		     ( *mount_handle )->key_data,
		     0,
		     16 ) == NULL )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_SET_FAILED,
			 "%s: unable to clear key data.",
			 function );

			result = -1;
		}
		memory_free(
		 *mount_handle );

		*mount_handle = NULL;
	}
	return( result );
}

/* Signals the mount handle to abort
 * Returns 1 if successful or -1 on error
 */
int mount_handle_signal_abort(
     mount_handle_t *mount_handle,
     libcerror_error_t **error )
{
	${library_name}_file_t *input_file = NULL;
	static char *function      = "mount_handle_signal_abort";	
	int input_file_index       = 0;
	int number_of_input_files  = 0;

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( libcdata_array_get_number_of_entries(
	     mount_handle->input_files_array,
	     &number_of_input_files,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of input files.",
		 function );

		return( -1 );
	}
	for( input_file_index = number_of_input_files - 1;
	     input_file_index > 0;
	     input_file_index-- )
	{
		if( libcdata_array_get_entry_by_index(
		     mount_handle->input_files_array,
		     input_file_index,
		     (intptr_t **) &input_file,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve input file: %d.",
			 function,
			 input_file_index );

			return( -1 );
		}
		if( ${library_name}_file_signal_abort(
		     input_file,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to signal input file: %d to abort.",
			 function,
			 input_file_index );

			return( -1 );
		}
	}
	return( 1 );
}

/* Sets the keys
 * Returns 1 if successful or -1 on error
 */
int mount_handle_set_keys(
     mount_handle_t *mount_handle,
     const system_character_t *string,
     libcerror_error_t **error )
{
	static char *function   = "mount_handle_set_keys";
	size_t string_length    = 0;
	uint32_t base16_variant = 0;

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	string_length = system_string_length(
	                 string );

	if( memory_set(
	     mount_handle->key_data,
	     0,
	     16 ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear key data.",
		 function );

		goto on_error;
	}
	base16_variant = LIBUNA_BASE16_VARIANT_RFC4648;

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	if( _BYTE_STREAM_HOST_IS_ENDIAN_BIG )
	{
		base16_variant |= LIBUNA_BASE16_VARIANT_ENCODING_UTF16_BIG_ENDIAN;
	}
	else
	{
		base16_variant |= LIBUNA_BASE16_VARIANT_ENCODING_UTF16_LITTLE_ENDIAN;
	}
#endif
	if( string_length != 32 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_UNSUPPORTED_VALUE,
		 "%s: unsupported string length.",
		 function );

		goto on_error;
	}
	if( libuna_base16_stream_copy_to_byte_stream(
	     (uint8_t *) string,
	     string_length,
	     mount_handle->key_data,
	     16,
	     base16_variant,
	     0,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_COPY_FAILED,
		 "%s: unable to copy key data.",
		 function );

		goto on_error;
	}
	mount_handle->key_data_is_set = 1;

	return( 1 );

on_error:
	memory_set(
	 mount_handle->key_data,
	 0,
	 16 );

	mount_handle->key_data_is_set = 0;

	return( -1 );
}

/* Sets the password
 * Returns 1 if successful or -1 on error
 */
int mount_handle_set_password(
     mount_handle_t *mount_handle,
     const system_character_t *string,
     libcerror_error_t **error )
{
	static char *function = "mount_handle_set_password";

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( string == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid string.",
		 function );

		return( -1 );
	}
	mount_handle->password        = string;
	mount_handle->password_length = system_string_length(
	                                 mount_handle->password );

	return( 1 );
}

/* Opens the input of the mount handle
 * Returns 1 if successful, 0 if the keys could not be read or -1 on error
 */
int mount_handle_open_input(
     mount_handle_t *mount_handle,
     const system_character_t *filename,
     libcerror_error_t **error )
{
	${library_name}_file_t *input_file       = NULL;
	system_character_t *basename_end = NULL;
	static char *function            = "mount_handle_open_input";
	size_t basename_length           = 0;
	size_t filename_length           = 0;
	int entry_index                  = 0;

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( filename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid filename.",
		 function );

		return( -1 );
	}
	filename_length = system_string_length(
	                   filename );

	basename_end = system_string_search_character_reverse(
	                filename,
	                (system_character_t) LIBCPATH_SEPARATOR,
	                filename_length + 1 );

	if( basename_end != NULL )
	{
		basename_length = (size_t) ( basename_end - filename ) + 1;
	}
	if( basename_length > 0 )
	{
		if( mount_handle_set_basename(
		     mount_handle,
		     filename,
		     basename_length,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set basename.",
			 function );

			goto on_error;
		}
	}
	if( ${library_name}_file_initialize(
	     &input_file,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize input file.",
		 function );

		goto on_error;
	}
	if( mount_handle->key_data_is_set != 0 )
	{
		if( ${library_name}_file_set_keys(
		     input_file,
		     mount_handle->key_data,
		     16,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set keys.",
			 function );

			goto on_error;
		}
	}
	else if( mount_handle->password != NULL )
	{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		if( ${library_name}_file_set_utf16_password(
		     input_file,
		     (uint16_t *) mount_handle->password,
		     mount_handle->password_length,
		     error ) != 1 )
#else
		if( ${library_name}_file_set_utf8_password(
		     input_file,
		     (uint8_t *) mount_handle->password,
		     mount_handle->password_length,
		     error ) != 1 )
#endif
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
			 "%s: unable to set password.",
			 function );

			goto on_error;
		}
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	if( ${library_name}_file_open_wide(
	     input_file,
	     filename,
	     ${library_name_upper_case}_OPEN_READ,
	     error ) != 1 )
#else
	if( ${library_name}_file_open(
	     input_file,
	     filename,
	     ${library_name_upper_case}_OPEN_READ,
	     error ) != 1 )
#endif
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open input file.",
		 function );

		goto on_error;
	}
/* TODO
	if( mount_handle_open_input_parent_file(
	     mount_handle,
	     input_file,
	     error ) == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open parent input file.",
		 function );

		goto on_error;
	}
*/
	if( libcdata_array_append_entry(
	     mount_handle->input_files_array,
	     &entry_index,
	     (intptr_t *) input_file,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_APPEND_FAILED,
		 "%s: unable to append input file to array.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( input_file != NULL )
	{
		${library_name}_file_free(
		 &input_file,
		 NULL );
	}
	libcdata_array_empty(
	 mount_handle->input_files_array,
	 (int (*)(intptr_t **, libcerror_error_t **)) &${library_name}_file_free,
	 NULL );

	return( -1 );
}

/* Closes the mount handle
 * Returns the 0 if succesful or -1 on error
 */
int mount_handle_close(
     mount_handle_t *mount_handle,
     libcerror_error_t **error )
{
	${library_name}_file_t *input_file = NULL;
	static char *function      = "mount_handle_close";
	int input_file_index       = 0;
	int number_of_input_files  = 0;

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( libcdata_array_get_number_of_entries(
	     mount_handle->input_files_array,
	     &number_of_input_files,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of input files.",
		 function );

		return( -1 );
	}
	for( input_file_index = number_of_input_files - 1;
	     input_file_index > 0;
	     input_file_index-- )
	{
		if( libcdata_array_get_entry_by_index(
		     mount_handle->input_files_array,
		     input_file_index,
		     (intptr_t **) &input_file,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve input file: %d.",
			 function,
			 input_file_index );

			return( -1 );
		}
		if( ${library_name}_file_close(
		     input_file,
		     error ) != 0 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_IO,
			 LIBCERROR_IO_ERROR_CLOSE_FAILED,
			 "%s: unable to close input file: %d.",
			 function,
			 input_file_index );

			return( -1 );
		}
	}
	return( 0 );
}

/* Read a buffer from a specific input file
 * Returns the number of bytes read if successful or -1 on error
 */
ssize_t mount_handle_read_buffer(
         mount_handle_t *mount_handle,
         int input_file_index,
         uint8_t *buffer,
         size_t size,
         libcerror_error_t **error )
{
	${library_name}_file_t *input_file = NULL;
	static char *function      = "mount_handle_read_buffer";
	ssize_t read_count         = 0;

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( libcdata_array_get_entry_by_index(
	     mount_handle->input_files_array,
	     input_file_index,
	     (intptr_t **) &input_file,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve input file: %d.",
		 function,
		 input_file_index );

		return( -1 );
	}
	read_count = ${library_name}_file_read_buffer(
	              input_file,
	              buffer,
	              size,
	              error );

	if( read_count == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read buffer from input file: %d.",
		 function,
		 input_file_index );

		return( -1 );
	}
	return( read_count );
}

/* Seeks a specific offset in a specific input file
 * Returns the offset if successful or -1 on error
 */
off64_t mount_handle_seek_offset(
         mount_handle_t *mount_handle,
         int input_file_index,
         off64_t offset,
         int whence,
         libcerror_error_t **error )
{
	${library_name}_file_t *input_file = NULL;
	static char *function      = "mount_handle_seek_offset";

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( libcdata_array_get_entry_by_index(
	     mount_handle->input_files_array,
	     input_file_index,
	     (intptr_t **) &input_file,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve input file: %d.",
		 function,
		 input_file_index );

		return( -1 );
	}
	offset = ${library_name}_file_seek_offset(
	          input_file,
	          offset,
	          whence,
	          error );

	if( offset == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_SEEK_FAILED,
		 "%s: unable to seek offset in input file: %d.",
		 function,
		 input_file_index );

		return( -1 );
	}
	return( offset );
}

/* Retrieves the media size of a specific input file
 * Returns 1 if successful or -1 on error
 */
int mount_handle_get_media_size(
     mount_handle_t *mount_handle,
     int input_file_index,
     size64_t *size,
     libcerror_error_t **error )
{
	${library_name}_file_t *input_file = NULL;
	static char *function      = "mount_handle_get_media_size";

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( libcdata_array_get_entry_by_index(
	     mount_handle->input_files_array,
	     input_file_index,
	     (intptr_t **) &input_file,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve input file: %d.",
		 function,
		 input_file_index );

		return( -1 );
	}
	if( ${library_name}_file_get_media_size(
	     input_file,
	     size,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve media size from input file: %d.",
		 function,
		 input_file_index );

		return( -1 );
	}
	return( 1 );
}

/* Retrieves the number of input files
 * Returns 1 if successful or -1 on error
 */
int mount_handle_get_number_of_input_files(
     mount_handle_t *mount_handle,
     int *number_of_input_files,
     libcerror_error_t **error )
{
	static char *function = "mount_handle_get_number_of_input_files";

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( libcdata_array_get_number_of_entries(
	     mount_handle->input_files_array,
	     number_of_input_files,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
		 "%s: unable to retrieve number of input files.",
		 function );

		return( -1 );
	}
	return( 1 );
}

/* Sets the basename
 * Returns 1 if successful or -1 on error
 */
int mount_handle_set_basename(
     mount_handle_t *mount_handle,
     const system_character_t *basename,
     size_t basename_size,
     libcerror_error_t **error )
{
	static char *function = "mount_handle_set_basename";

	if( mount_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid mount handle.",
		 function );

		return( -1 );
	}
	if( basename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid basename.",
		 function );

		return( -1 );
	}
	if( basename_size == 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_MISSING,
		 "%s: missing basename.",
		 function );

		goto on_error;
	}
	if( ( basename_size > (size_t) SSIZE_MAX )
	 || ( ( sizeof( system_character_t ) * basename_size ) > (size_t) SSIZE_MAX ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid basename size value exceeds maximum.",
		 function );

		goto on_error;
	}
	if( mount_handle->basename != NULL )
	{
		memory_free(
		 mount_handle->basename );

		mount_handle->basename      = NULL;
		mount_handle->basename_size = 0;
	}
	mount_handle->basename = system_string_allocate(
	                          basename_size );

	if( mount_handle->basename == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create basename string.",
		 function );

		goto on_error;
	}
	if( system_string_copy(
	     mount_handle->basename,
	     basename,
	     basename_size ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_COPY_FAILED,
		 "%s: unable to copy basename.",
		 function );

		goto on_error;
	}
	mount_handle->basename[ basename_size - 1 ] = 0;

	mount_handle->basename_size = basename_size;

	return( 1 );

on_error:
	if( mount_handle->basename != NULL )
	{
		memory_free(
		 mount_handle->basename );

		mount_handle->basename = NULL;
	}
	mount_handle->basename_size = 0;

	return( -1 );
}

