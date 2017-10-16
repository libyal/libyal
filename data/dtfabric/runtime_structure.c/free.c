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

