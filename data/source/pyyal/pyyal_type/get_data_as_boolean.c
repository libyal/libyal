/* Retrieves the data as a boolean value
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_data_as_boolean(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name:upper_case}_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${python_module_name}_${type_name}_get_data_as_boolean";
	uint8_t value_boolean    = 0;
	int result               = 0;

	${python_module_name:upper_case}_UNREFERENCED_PARAMETER( arguments )

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_data_as_boolean(
		  ${python_module_name}_${type_name}->${type_name},
		  &value_boolean,
		  &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve boolean value.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	if( value_boolean != 0x00 )
	{
		Py_IncRef(
		 Py_True );

		return( Py_True );
	}
	Py_IncRef(
	 Py_False );

	return( Py_False );
}

