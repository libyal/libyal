/*
 * Mount tool dokan functions
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

#include <common.h>
#include <memory.h>
#include <types.h>
#include <wide_string.h>

#include "mount_dokan.h"
#include "mount_file_entry.h"
#include "mount_handle.h"
#include "${tools_name}_libcerror.h"
#include "${tools_name}_libcnotify.h"
#include "${tools_name}_${library_name}.h"
#include "${tools_name}_unused.h"

extern mount_handle_t *${mount_tool_name}_mount_handle;

#if defined( HAVE_LIBDOKAN )

#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
#define MOUNT_DOKAN_ERROR_BAD_ARGUMENTS -ERROR_BAD_ARGUMENTS
#define MOUNT_DOKAN_ERROR_FILE_NOT_FOUND -ERROR_FILE_NOT_FOUND
#define MOUNT_DOKAN_ERROR_GENERIC_FAILURE -ERROR_GEN_FAILURE
#define MOUNT_DOKAN_ERROR_READ_FAULT -ERROR_READ_FAULT

#else
#define MOUNT_DOKAN_ERROR_BAD_ARGUMENTS STATUS_UNSUCCESSFUL
#define MOUNT_DOKAN_ERROR_FILE_NOT_FOUND STATUS_OBJECT_NAME_NOT_FOUND
#define MOUNT_DOKAN_ERROR_GENERIC_FAILURE STATUS_UNSUCCESSFUL
#define MOUNT_DOKAN_ERROR_READ_FAULT STATUS_UNEXPECTED_IO_ERROR

#endif /* ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 ) */

#if defined( HAVE_DOKAN_LONG_PATHS )
#define DOKAN_MAX_PATH 32768
#else
#define DOKAN_MAX_PATH MAX_PATH
#endif

/* Sets the values in a file information structure
 * The time values contain an unsigned 64-bit FILETIME timestamp
 * Returns 1 if successful or -1 on error
 */
int mount_dokan_set_file_information(
     BY_HANDLE_FILE_INFORMATION *file_information,
     size64_t size,
     uint16_t file_mode,
     uint64_t creation_time,
     uint64_t access_time,
     uint64_t modification_time,
     libcerror_error_t **error )
{
	static char *function = "mount_dokan_set_file_information";

	if( file_information == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file information.",
		 function );

		return( -1 );
	}
	if( size > 0 )
	{
		file_information->nFileSizeHigh = (DWORD) ( size >> 32 );
		file_information->nFileSizeLow  = (DWORD) ( size & 0xffffffffUL );
	}
	if( ( file_mode & 0x4000 ) != 0 )
	{
		file_information->dwFileAttributes = FILE_ATTRIBUTE_DIRECTORY;
	}
	else
	{
		file_information->dwFileAttributes = FILE_ATTRIBUTE_NORMAL;
	}
	file_information->ftCreationTime.dwLowDateTime  = (uint32_t) ( creation_time & 0x00000000ffffffffULL );
	file_information->ftCreationTime.dwHighDateTime = creation_time >> 32;

	file_information->ftLastAccessTime.dwLowDateTime  = (uint32_t) ( access_time & 0x00000000ffffffffULL );
	file_information->ftLastAccessTime.dwHighDateTime = access_time >> 32;

	file_information->ftLastWriteTime.dwLowDateTime  = (uint32_t) ( modification_time & 0x00000000ffffffffULL );
	file_information->ftLastWriteTime.dwHighDateTime = modification_time >> 32;

	return( 1 );
}

/* Sets the values in a find data structure
 * The time values contain an unsigned 64-bit FILETIME timestamp
 * Returns 1 if successful or -1 on error
 */
int mount_dokan_set_find_data(
     WIN32_FIND_DATAW *find_data,
     size64_t size,
     uint16_t file_mode,
     uint64_t creation_time,
     uint64_t access_time,
     uint64_t modification_time,
     libcerror_error_t **error )
{
	static char *function = "mount_dokan_set_find_data";

	if( find_data == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid find data.",
		 function );

		return( -1 );
	}
	if( size > 0 )
	{
		find_data->nFileSizeHigh = (DWORD) ( size >> 32 );
		find_data->nFileSizeLow  = (DWORD) ( size & 0xffffffffUL );
	}
	if( ( file_mode & 0x4000 ) != 0 )
	{
		find_data->dwFileAttributes = FILE_ATTRIBUTE_DIRECTORY;
	}
	else
	{
		find_data->dwFileAttributes = FILE_ATTRIBUTE_NORMAL;
	}
	find_data->ftCreationTime.dwLowDateTime  = (uint32_t) ( creation_time & 0x00000000ffffffffULL );
	find_data->ftCreationTime.dwHighDateTime = creation_time >> 32;

	find_data->ftLastAccessTime.dwLowDateTime  = (uint32_t) ( access_time & 0x00000000ffffffffULL );
	find_data->ftLastAccessTime.dwHighDateTime = access_time >> 32;

	find_data->ftLastWriteTime.dwLowDateTime  = (uint32_t) ( modification_time & 0x00000000ffffffffULL );
	find_data->ftLastWriteTime.dwHighDateTime = modification_time >> 32;

	return( 1 );
}

/* Fills a directory entry
 * Returns 1 if successful or -1 on error
 */
int mount_dokan_filldir(
     PFillFindData fill_find_data,
     DOKAN_FILE_INFO *file_info,
     wchar_t *name,
     size_t name_size,
     WIN32_FIND_DATAW *find_data,
     mount_file_entry_t *file_entry,
     libcerror_error_t **error )
{
	static char *function      = "mount_dokan_filldir";
	size64_t file_size         = 0;
	uint64_t access_time       = 0;
	uint64_t creation_time     = 0;
	uint64_t modification_time = 0;
	uint16_t file_mode         = 0;

	if( fill_find_data == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid fill find data.",
		 function );

		return( -1 );
	}
	if( name == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid name.",
		 function );

		return( -1 );
	}
	if( name_size > (size_t) DOKAN_MAX_PATH )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_OUT_OF_BOUNDS,
		 "%s: invalid name size value out of bounds.",
		 function );

		return( -1 );
	}
	if( file_entry != NULL )
	{
		if( mount_file_entry_get_size(
		     file_entry,
		     &file_size,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve file entry size.",
			 function );

			return( -1 );
		}
		if( mount_file_entry_get_file_mode(
		     file_entry,
		     &file_mode,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve file mode.",
			 function );

			return( -1 );
		}
		if( mount_file_entry_get_creation_time(
		     file_entry,
		     &creation_time,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve creation time.",
			 function );

			return( -1 );
		}
		if( mount_file_entry_get_access_time(
		     file_entry,
		     &access_time,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve access time.",
			 function );

			return( -1 );
		}
		if( mount_file_entry_get_modification_time(
		     file_entry,
		     &modification_time,
		     error ) != 1 )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_GET_FAILED,
			 "%s: unable to retrieve modification time.",
			 function );

			return( -1 );
		}
	}
	if( memory_set(
	     find_data,
	     0,
	     sizeof( WIN32_FIND_DATAW ) ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear find data.",
		 function );

		return( -1 );
	}
	if( wide_string_copy(
	     find_data->cFileName,
	     name,
	     name_size ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
		 "%s: unable to copy filename.",
		 function );

		return( -1 );
	}
	if( name_size <= (size_t) 14 )
	{
		if( wide_string_copy(
		     find_data->cAlternateFileName,
		     name,
		     name_size ) == NULL )
		{
			libcerror_error_set(
			 error,
			 LIBCERROR_ERROR_DOMAIN_MEMORY,
			 LIBCERROR_MEMORY_ERROR_COPY_FAILED,
			 "%s: unable to copy alternate filename.",
			 function );

			return( -1 );
		}
	}
	if( mount_dokan_set_find_data(
	     find_data,
	     file_size,
	     file_mode,
	     creation_time,
	     access_time,
	     modification_time,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set find data.",
		 function );

		return( -1 );
	}
	if( fill_find_data(
	     find_data,
	     file_info ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set directory entry.",
		 function );

		return( -1 );
	}
	return( 1 );
}

