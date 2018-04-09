/* Retrieves the ${value_description_long}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_${value_name}(
           ${python_module_name}_${base_type_name}_t *${python_module_name}_${base_type_name},
           PyObject *arguments ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *integer_object = NULL;
	libcerror_error_t *error = NULL;
	static char *function    = "${python_module_name}_${type_name}_get_${value_name}";
	uint32_t value_32bit     = 0;
	int result               = 0;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( arguments )

	if( ${python_module_name}_${base_type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${base_type_description}.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_${value_name}(
	          ${python_module_name}_${base_type_name}->${base_type_name},
	          &value_32bit,
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

		return( NULL );
	}
	integer_object = PyLong_FromUnsignedLong(
	                  (unsigned long) value_32bit );

	return( integer_object );
}

