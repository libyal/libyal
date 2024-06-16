/* Retrieves the data as an integer value
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_data_as_integer(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name:upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *integer_object = NULL;
	libcerror_error_t *error = NULL;
	static char *function    = "${python_module_name}_${type_name}_get_data_as_integer";
	int64_t integer_value    = 0;
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

	result = ${library_name}_${type_name}_get_data_as_integer(
	          ${python_module_name}_${type_name}->${type_name},
	          &integer_value,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve data as integer value.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
#warning "This is generated code make sure to implement this functionality."
	integer_object = ${python_module_name}_integer_signed_new_from_64bit(
	                  integer_value );

	return( integer_object );
}

