/* Retrieves the format version
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_format_version(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name:upper_case}_ATTRIBUTE_UNUSED )
{
	char utf8_string[ 4 ];

	PyObject *string_object     = NULL;
	libcerror_error_t *error    = NULL;
	static char *function       = "${python_module_name}_${type_name}_get_format_version";
	${value_type} major_version = 0;
	${value_type} minor_version = 0;
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

	result = ${library_name}_${type_name}_get_format_version(
	          ${python_module_name}_${type_name}->${type_name},
	          &major_version,
	          &minor_version,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve format version.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	if( major_version > 9 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: major version out of bounds.",
		 function );

		return( NULL );
	}
	if( minor_version > 9 )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: minor version out of bounds.",
		 function );

		return( NULL );
	}
	utf8_string[ 0 ] = '0' + (char) major_version;
	utf8_string[ 1 ] = '.';
	utf8_string[ 2 ] = '0' + (char) minor_version;
	utf8_string[ 3 ] = 0;

	/* Pass the string length to PyUnicode_DecodeUTF8 otherwise it makes
	 * the end of string character is part of the string.
	 */
	string_object = PyUnicode_DecodeUTF8(
	                 utf8_string,
	                 (Py_ssize_t) 3,
	                 NULL );

	if( string_object == NULL )
	{
		PyErr_Format(
		 PyExc_IOError,
		 "%s: unable to convert UTF-8 string into Unicode object.",
		 function );

		return( NULL );
	}
	return( string_object );
}

