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

