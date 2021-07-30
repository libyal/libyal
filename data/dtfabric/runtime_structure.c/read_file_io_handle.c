/* Reads the ${structure_description}
 * Returns 1 if successful or -1 on error
 */
int ${library_name}_${structure_name}_read_file_io_handle(
     ${library_name}_${structure_name}_t *${structure_name},
     libbfio_handle_t *file_io_handle,
     off64_t file_offset,
     libcerror_error_t **error )
{
	uint8_t ${structure_name}_data[ sizeof( ${prefix}_${structure_name}_t ) ];

	static char *function = "${library_name}_${structure_name}_read_file_io_handle";
	ssize_t read_count    = 0;

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
	read_count = libbfio_handle_read_buffer_at_offset(
	              file_io_handle,
	              ${structure_name}_data,
	              sizeof( ${prefix}_${structure_name}_t ),
	              file_offset,
	              error );

	if( read_count != (ssize_t) sizeof( ${prefix}_${structure_name}_t ) )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read ${structure_description} data at offset: %" PRIi64 " (0x%08" PRIx64 ").",
		 function,
		 file_offset,
		 file_offset );

		return( -1 );
	}
	if( ${library_name}_${structure_name}_read_data(
	     ${structure_name},
	     ${structure_name}_data,
	     sizeof( ${prefix}_${structure_name}_t ),
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_READ_FAILED,
		 "%s: unable to read ${structure_description}.",
		 function );

		return( -1 );
	}
	return( 1 );
}

