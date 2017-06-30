/*
 * ${structure_description_title} functions
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

#include <common.h>
#include <byte_stream.h>
#include <memory.h>
#include <types.h>

#include "${library_name}_libcerror.h"
#include "${library_name}_libcnotify.h"
#include "${library_name}_${structure_name}.h"

#include "${prefix}_${structure_name}.h"

/* Creates a ${structure_description}
 * Make sure the value ${structure_name} is referencing, is set to NULL
 * Returns 1 if successful or -1 on error
 */
int ${library_name}_${structure_name}_initialize(
     ${library_name}_${structure_name}_t **${structure_name},
     libcerror_error_t **error )
{
	static char *function = "${library_name}_${structure_name}_initialize";

	if( ${structure_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${structure_description}.",
		 function );

		return( -1 );
	}
	if( *${structure_name} != NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_ALREADY_SET,
		 "%s: invalid ${structure_description} value already set.",
		 function );

		return( -1 );
	}
	*${structure_name} = memory_allocate_structure(
	              ${library_name}_${structure_name}_t );

	if( *${structure_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_INSUFFICIENT,
		 "%s: unable to create ${structure_description}.",
		 function );

		goto on_error;
	}
	if( memory_set(
	     *${structure_name},
	     0,
	     sizeof( ${library_name}_${structure_name}_t ) ) == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_MEMORY,
		 LIBCERROR_MEMORY_ERROR_SET_FAILED,
		 "%s: unable to clear ${structure_description}.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( *${structure_name} != NULL )
	{
		memory_free(
		 *${structure_name} );

		*${structure_name} = NULL;
	}
	return( -1 );
}

/* Frees a ${structure_description}
 * Returns 1 if successful or -1 on error
 */
int ${library_name}_${structure_name}_free(
     ${library_name}_${structure_name}_t **${structure_name},
     libcerror_error_t **error )
{
	static char *function = "${library_name}_${structure_name}_free";

	if( ${structure_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${structure_description}.",
		 function );

		return( -1 );
	}
	if( *${structure_name} != NULL )
	{
		memory_free(
		 *${structure_name} );

		*${structure_name} = NULL;
	}
	return( 1 );
}

/* Reads the ${structure_description} data
 * Returns 1 if successful or -1 on error
 */
int ${library_name}_${structure_name}_read_data(
     ${library_name}_${structure_name}_t *${structure_name},
     const uint8_t *data,
     size_t data_size,
     libcerror_error_t **error )
{
	static char *function                 = "${library_name}_${structure_name}_read_data";
	uint16_t number_of_relocation_entries = 0;
	uint16_t relocation_table_offset      = 0;

#if defined( HAVE_DEBUG_OUTPUT )
	uint32_t value_32bit                  = 0;
	uint16_t value_16bit                  = 0;
#endif

	if( ${structure_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${structure_description}.",
		 function );

		return( -1 );
	}
	if( data == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid data.",
		 function );

		return( -1 );
	}
	if( data_size < sizeof( ${prefix}_${structure_name}_t ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_VALUE_TOO_SMALL,
		 "%s: invalid data size value too small.",
		 function );

		return( -1 );
	}
	if( data_size > (size_t) SSIZE_MAX )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_VALUE_EXCEEDS_MAXIMUM,
		 "%s: invalid data size value exceeds maximum.",
		 function );

		return( -1 );
	}
#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
		libcnotify_printf(
		 "%s: ${structure_description}:\n",
		 function );
		libcnotify_print_data(
		 data,
		 sizeof( ${prefix}_${structure_name}_t ),
		 0 );
	}
#endif
	if( memory_compare(
	     ( (${prefix}_${structure_name}_t *) data )->signature,
	     EXE_MZ_SIGNATURE,
	     2 ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_UNSUPPORTED_VALUE,
		 "%s: invalid signature.",
		 function );

		return( -1 );
	}
${structure_members_copy_from_byte_stream}

#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
${structure_members_debug_print}

		libcnotify_printf(
		 "\n" );
	}
#endif
	return( 1 );
}

/* Reads the ${structure_description} from a Basic File IO (bfio) handle
 * Returns 1 if successful or -1 on error
 */
int ${library_name}_${structure_name}_read_file_io_handle(
     ${library_name}_${structure_name}_t *${structure_name},
     libbfio_handle_t *file_io_handle,
     off64_t file_offset,
     libcerror_error_t **error )
{
	uint8_t data[ sizeof( ${prefix}_${structure_name}_t ) ];

	static char *function = "${library_name}_${structure_name}_read_file_io_handle";
	ssize_t read_count    = 0;

#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
		libcnotify_printf(
		 "%s: reading ${structure_description} at offset: %" PRIi64 " (0x%08" PRIx64 ")\n",
		 function,
		 file_offset,
		 file_offset );
	}
#endif
	if( libbfio_handle_seek_offset(
	     file_io_handle,
	     file_offset,
	     SEEK_SET,
	     error ) == -1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_SEEK_FAILED,
		 "%s: unable to seek ${structure_description} offset: %" PRIi64 " (0x%08" PRIx64 ").",
		 function,
		 file_offset,
		 file_offset );

		return( -1 );
	}
	read_count = libbfio_handle_read_buffer(
	              file_io_handle,
	              data,
	              sizeof( ${prefix}_${structure_name}_t ),
	              error );

	if( read_count != (ssize_t) sizeof( ${prefix}_${structure_name}_t ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read ${structure_description} at offset: %" PRIi64 " (0x%08" PRIx64 ").",
		 function,
		 file_offset,
		 file_offset );

		return( -1 );
	}
	if( ${library_name}_${structure_name}_read_data(
	     ${structure_name},
	     data,
	     sizeof( ${prefix}_${structure_name}_t ),
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read ${structure_description} at offset: %" PRIi64 " (0x%08" PRIx64 ").",
		 function,
		 file_offset,
		 file_offset );

		return( -1 );
	}
	return( 1 );
}

