/* Retrieves the ${value_description_long}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_${value_name}(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name:upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *${value_name}_object                 = NULL;
	${library_name}_${value_type}_t *${value_name} = NULL;
	libcerror_error_t *error                       = NULL;
	static char *function                          = "${python_module_name}_${type_name}_get_${value_name}";
	int result                                     = 0;

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

	result = ${library_name}_${type_name}_get_${value_name}(
	          ${python_module_name}_${type_name}->${type_name},
	          &${value_name},
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve ${value_description}.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	${value_name}_object = ${python_module_name}_${value_type}_new(
	                        ${value_name},
	                        (PyObject *) ${python_module_name}_${type_name} );

	if( ${value_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create ${value_description} object.",
		 function );

		goto on_error;
	}
	return( ${value_name}_object );

on_error:
	if( ${value_name} != NULL )
	{
		${library_name}_${value_type}_free(
		 &${value_name},
		 NULL );
	}
	return( NULL );
}

