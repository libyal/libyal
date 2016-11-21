/* Sets the ${value_description}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_set_${type_name}(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *bytes_object      = NULL;
	libcerror_error_t *error    = NULL;
	char *data                  = NULL;
	static char *function       = "${python_module_name}_${type_name}_set_${type_name}";
	static char *keyword_list[] = { "${type_name}", NULL };
        Py_ssize_t data_size        = 0;
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
	     "O",
	     keyword_list,
	     &bytes_object ) == 0 )
	{
		return( NULL );
	}
#if PY_MAJOR_VERSION >= 3
	data = PyBytes_AsString(
	        bytes_object );

	data_size = PyBytes_Size(
	             bytes_object );
#else
	data = PyString_AsString(
	        bytes_object );

	data_size = PyString_Size(
	             bytes_object );
#endif
	if( ( data_size < 0 )
	 || ( data_size > (Py_ssize_t) SSIZE_MAX ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid data size value out of bounds.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_set_${value_name}(
	          ${python_module_name}_${type_name}->${type_name},
	          (uint8_t *) data,
	          (size_t) data_size,
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

