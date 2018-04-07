/* Retrieves the number of recovered ${value_description_long}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_number_of_recovered_${value_name}(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *integer_object    = NULL;
	libcerror_error_t *error    = NULL;
	static char *function       = "${python_module_name}_${type_name}_get_number_of_recovered_${value_name}";
	int number_of_${value_name} = 0;
	int result                  = 0;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( arguments )

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_number_of_recovered_${value_name}(
	          ${python_module_name}_${type_name}->${type_name},
	          &number_of_${value_name},
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve number of recovered ${value_description}.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
#if PY_MAJOR_VERSION >= 3
	integer_object = PyLong_FromLong(
	                  (long) number_of_${value_name} );
#else
	integer_object = PyInt_FromLong(
	                  (long) number_of_${value_name} );
#endif
	return( integer_object );
}

