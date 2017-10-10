/* Test ${value_name} compare function
 * Returns LIBCDATA_COMPARE_LESS, LIBCDATA_COMPARE_EQUAL, LIBCDATA_COMPARE_GREATER if successful or -1 on error
 */
int ${library_name_suffix}_test_${type_name}_${value_name}_compare_function(
     intptr_t *first_${value_name},
     intptr_t *second_${value_name},
     lib${library_name_suffix}_error_t **error )
{
	static char *function = "${library_name_suffix}_test_${type_name}_${value_name}_compare_function";

	if( first_${value_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid first ${value_name}.",
		 function );

		return( -1 );
	}
	if( second_${value_name} == NULL )
	{
		libcerror_error_set(
		 error,
		 LIBCERROR_ERROR_DOMAIN_ARGUMENTS,
		 LIBCERROR_ARGUMENT_ERROR_INVALID_VALUE,
		 "%s: invalid second ${value_name}.",
		 function );

		return( -1 );
	}
/* TODO implement */
	return( LIBCDATA_COMPARE_EQUAL );
}

