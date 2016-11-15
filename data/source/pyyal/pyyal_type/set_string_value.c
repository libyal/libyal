/* Sets the ${value_description}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_set_${value_name}(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	libcerror_error_t *error    = NULL;
	static char *function       = "${python_module_name}_${type_name}_set_${value_name}";
	static char *keyword_list[] = { "${value_name}", NULL };
	char *utf8_string           = NULL;
	size_t utf8_string_length   = 0;
	int result                  = 0;

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	if( PyArg_ParseTupleAndKeywords(
	     arguments,
	     keywords,
	     "s",
	     keyword_list,
	     &utf8_string ) == 0 )
	{
		return( NULL );
	}
	if( utf8_string == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${value_description}.",
		 function );

		return( NULL );
	}
	utf8_string_length = narrow_string_length(
	                      utf8_string );

	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_set_utf8_${value_name}(
	          ${python_module_name}_${type_name}->${type_name},
	          (uint8_t *) utf8_string,
	          utf8_string_length,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to set ${value_description}.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );
}

