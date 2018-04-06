/* Retrieves the sub ${value_description} specified by the path
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_sub_${value_name}_by_path(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *${value_name}_object                     = NULL;
	libcerror_error_t *error                           = NULL;
	${library_name}_${value_type}_t *sub_${value_name} = NULL;
	static char *function                              = "${python_module_name}_${type_name}_get_sub_${value_name}_by_path";
	static char *keyword_list[]                        = { "path", NULL };
	char *utf8_path                                    = NULL;
	size_t utf8_path_length                            = 0;
	int result                                         = 0;

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
	     &utf8_path ) == 0 )
	{
		goto on_error;
	}
	utf8_path_length = narrow_string_length(
	                    utf8_path );

	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_sub_${value_name}_by_utf8_path(
	           ${python_module_name}_${type_name}->${type_name},
	           (uint8_t *) utf8_path,
	           utf8_path_length,
	           &sub_${value_name},
	           &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve sub ${value_description}.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	else if( result == 0 )
	{
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	${value_name}_object = ${python_module_name}_${value_type}_new(
	                        sub_${value_name},
	                        ${python_module_name}_${value_name}->parent_object );

	if( ${value_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create sub ${value_type_description} object.",
		 function );

		goto on_error;
	}
	return( ${value_name}_object );

on_error:
	if( sub_${value_name} != NULL )
	{
		${library_name}_${value_type}_free(
		 &sub_${value_name},
		 NULL );
	}
	return( NULL );
}

