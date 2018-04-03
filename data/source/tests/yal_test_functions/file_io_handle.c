/* Creates a file IO handle for test data
 * Returns 1 if successful or -1 on error
 */
int ${library_name_suffix}_test_open_file_io_handle(
     libbfio_handle_t **file_io_handle,
     uint8_t *data,
     size_t data_size,
     libcerror_error_t **error )
{
	static char *function = "${library_name_suffix}_test_open_file_io_handle";

	if( file_io_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file IO handle.",
		 function );

		return( -1 );
	}
	if( libbfio_memory_range_initialize(
	     file_io_handle,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to create file IO handle.",
		 function );

		goto on_error;
	}
	if( libbfio_memory_range_set(
	     *file_io_handle,
	     data,
	     data_size,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_SET_FAILED,
		 "%s: unable to set memory range of file IO handle.",
		 function );

		goto on_error;
	}
	if( libbfio_handle_open(
	     *file_io_handle,
	     LIBBFIO_OPEN_READ,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open file IO handle.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( *file_io_handle != NULL )
	{
		libbfio_handle_free(
		 file_io_handle,
		 NULL );
	}
	return( -1 );
}

/* Closes a file IO handle for test data
 * Returns 0 if successful or -1 on error
 */
int ${library_name_suffix}_test_close_file_io_handle(
     libbfio_handle_t **file_io_handle,
     libcerror_error_t **error )
{
	static char *function = "${library_name_suffix}_test_close_file_io_handle";
	int result            = 0;

	if( file_io_handle == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file IO handle.",
		 function );

		return( -1 );
	}
	if( libbfio_handle_close(
	     *file_io_handle,
	     error ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_CLOSE_FAILED,
		 "%s: unable to close file IO handle.",
		 function );

		result = -1;
	}
	if( libbfio_handle_free(
	     file_io_handle,
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
		 "%s: unable to free file IO handle.",
		 function );

		result = -1;
	}
	return( result );
}

