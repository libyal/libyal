/* Creates and opens a source ${type_name}
 * Returns 1 if successful or -1 on error
 */
int ${library_name_suffix}_test_${type_name}_open_source(
     ${library_name}_${type_name}_t **${type_name},
${test_options_function_arguments},
     libcerror_error_t **error )
{
	static char *function = "${library_name_suffix}_test_${type_name}_open_source";
${test_options_function_variables}

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
	if( file_io_${bfio_type} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid file IO ${bfio_type}.",
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
