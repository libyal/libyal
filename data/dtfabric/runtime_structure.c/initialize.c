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
	${memory_allocate_indentation} ${library_name}_${structure_name}_t );

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

