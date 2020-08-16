/* Initializes a ${type_description} object
 * Returns 0 if successful or -1 on error
 */
int ${python_module_name}_${type_name}_init(
     ${python_module_name}_${type_name}_t *${python_module_name}_${type_name} )
{
	static char *function = "${python_module_name}_${type_name}_init";

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return( -1 );
	}
	/* Make sure ${library_name} ${type_description} is set to NULL
	 */
	${python_module_name}_${type_name}->${type_name} = NULL;

	PyErr_Format(
	 PyExc_NotImplementedError,
	 "%s: initialize of ${type_description} not supported.",
	 function );

	return( -1 );
}

