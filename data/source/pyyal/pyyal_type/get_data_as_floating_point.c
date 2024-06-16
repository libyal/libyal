/* Retrieves the data as an floating-point value
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_data_as_floating_point(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name:upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *float_object      = NULL;
	libcerror_error_t *error    = NULL;
	static char *function       = "${python_module_name}_${type_name}_get_data_as_floating_point";
	double floating_point_value = 0;
	int result                  = 0;

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

	result = ${library_name}_${type_name}_get_data_as_floating_point(
	          ${python_module_name}_${type_name}->${type_name},
	          &floating_point_value,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve data as floating-point value.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	float_object = PyFloat_FromDouble(
	                floating_point_value );

	return( float_object );
}

