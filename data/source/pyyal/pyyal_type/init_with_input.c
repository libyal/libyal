/* Intializes a ${type_description} object
 * Returns 0 if successful or -1 on error
 */
int ${python_module_name}_${type_name}_init(
     ${python_module_name}_${type_name}_t *${python_module_name}_${type_name} )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${python_module_name}_${type_name}_init";

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return( -1 );
	}
	${python_module_name}_${type_name}->${type_name}   = NULL;
	${python_module_name}_${type_name}->file_io_handle = NULL;

	if( ${library_name}_${type_name}_initialize(
	     &( ${python_module_name}_${type_name}->${type_name} ),
	     &error ) != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_MemoryError,
		 "%s: unable to initialize ${type_description}.",
		 function );

		libcerror_error_free(
		 &error );

		return( -1 );
	}
	return( 0 );
}

