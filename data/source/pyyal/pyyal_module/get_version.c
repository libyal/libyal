/* Retrieves the ${python_module_name}/${library_name} version
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_get_version(
           PyObject *self ${python_module_name_upper_case}_ATTRIBUTE_UNUSED,
           PyObject *arguments ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	const char *errors           = NULL;
	const char *version_string   = NULL;
	size_t version_string_length = 0;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( self )
	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( arguments )

	Py_BEGIN_ALLOW_THREADS

	version_string = ${library_name}_get_version();

	Py_END_ALLOW_THREADS

	version_string_length = narrow_string_length(
	                         version_string );

	/* Pass the string length to PyUnicode_DecodeUTF8
	 * otherwise it makes the end of string character is part
	 * of the string
	 */
	return( PyUnicode_DecodeUTF8(
	         version_string,
	         (Py_ssize_t) version_string_length,
	         errors ) );
}

