/* Determines if the ${type_description} is ${value_description}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_is_${value_name}(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments PYREGF_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${python_module_name}_${type_name}_is_${value_name}";
	int result               = 0;

	PYREGF_UNREFERENCED_PARAMETER( arguments )

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_is_${value_name}(
	          ${python_module_name}_${type_name}->${type_name},
	          &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to determine if ${type_description} is ${value_description}.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	if( result != 0 )
	{
		Py_IncRef(
		 (PyObject *) Py_True );

		return( Py_True );
	}
	Py_IncRef(
	 (PyObject *) Py_False );

	return( Py_False );
}

