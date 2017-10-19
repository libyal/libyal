#if !defined( ${library_name_upper_case}_HAVE_BFIO )

extern \
int ${library_name}_file_open_file_io_handle(
     ${library_name}_file_t *file,
     libbfio_handle_t *file_io_handle,
     int access_flags,
     ${library_name}_error_t **error );

#endif /* !defined( ${library_name_upper_case}_HAVE_BFIO ) */

#if defined( HAVE_WIDE_SYSTEM_CHARACTER ) && SIZEOF_WCHAR_T != 2 && SIZEOF_WCHAR_T != 4
#error Unsupported size of wchar_t
#endif

/* Define to make ${library_name_suffix}_test_${type_name} generate verbose output
#define ${library_name_suffix_upper_case}_TEST_${type_name_upper_case}_VERBOSE
 */

/* Creates and opens a source ${type_name}
 * Returns 1 if successful or -1 on error
 */
int ${library_name_suffix}_test_${type_name}_open_source(
     ${library_name}_${type_name}_t **${type_name},
     libbfio_handle_t *file_io_handle,
     libcerror_error_t **error )
{
	static char *function = "${library_name_suffix}_test_${type_name}_open_source";
	int result            = 0;

	if( ${type_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${type_name}.",
		 function );

		return( -1 );
	}
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
	if( ${library_name}_${type_name}_initialize(
	     ${type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_INITIALIZE_FAILED,
		 "%s: unable to initialize ${type_name}.",
		 function );

		goto on_error;
	}
	result = ${library_name}_${type_name}_open_file_io_handle(
	          *${type_name},
	          file_io_handle,
	          ${library_name_upper_case}_OPEN_READ,
	          error );

	if( result != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_OPEN_FAILED,
		 "%s: unable to open ${type_name}.",
		 function );

		goto on_error;
	}
	return( 1 );

on_error:
	if( *${type_name} != NULL )
	{
		${library_name}_${type_name}_free(
		 ${type_name},
		 NULL );
	}
	return( -1 );
}

/* Closes and frees a source ${type_name}
 * Returns 1 if successful or -1 on error
 */
int ${library_name_suffix}_test_${type_name}_close_source(
     ${library_name}_${type_name}_t **${type_name},
     libcerror_error_t **error )
{
	static char *function = "${library_name_suffix}_test_${type_name}_close_source";
	int result            = 0;

	if( ${type_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid ${type_name}.",
		 function );

		return( -1 );
	}
	if( ${library_name}_${type_name}_close(
	     *${type_name},
	     error ) != 0 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_IO,
		 LIBCERROR_IO_ERROR_CLOSE_FAILED,
		 "%s: unable to close ${type_name}.",
		 function );

		result = -1;
	}
	if( ${library_name}_${type_name}_free(
	     ${type_name},
	     error ) != 1 )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_RUNTIME,
		 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
		 "%s: unable to free ${type_name}.",
		 function );

		result = -1;
	}
	return( result );
}

