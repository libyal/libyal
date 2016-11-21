/* Copies the ${type_description} from a ${value_description}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_copy_from_${value_name}(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *bytes_object        = NULL;
	libcerror_error_t *error      = NULL;
	const char *${value_name}     = NULL;
	static char *function         = "${python_module_name}_${type_name}_copy_from_${value_name}";
	static char *keyword_list[]   = { "${value_name}", NULL };
	Py_ssize_t ${value_name}_size = 0;
	int result                    = 0;

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_TypeError,
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
	PyErr_Clear();

#if PY_MAJOR_VERSION >= 3
	result = PyObject_IsInstance(
		  bytes_object,
		  (PyObject *) &PyBytes_Type );
#else
	result = PyObject_IsInstance(
		  bytes_object,
		  (PyObject *) &PyString_Type );
#endif
	if( result == -1 )
	{
		${python_module_name}_error_fetch_and_raise(
	         PyExc_RuntimeError,
		 "%s: unable to determine if object is of type bytes.",
		 function );

		return( NULL );
	}
	else if( result == 0 )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: unsupported bytes object type",
		 function );

		return( NULL );
	}
	PyErr_Clear();

#if PY_MAJOR_VERSION >= 3
	${value_name} = PyBytes_AsString(
	               bytes_object );

	${value_name}_size = PyBytes_Size(
	                    bytes_object );
#else
	${value_name} = PyString_AsString(
	               bytes_object );

	${value_name}_size = PyString_Size(
	                    bytes_object );
#endif
	if( ( ${value_name}_size < 0 )
	 || ( ${value_name}_size > (Py_ssize_t) SSIZE_MAX ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${value_description} size value out of bounds.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_copy_from_${value_name}(
	          ${python_module_name}_${type_name}->${type_name},
	          (uint8_t *) ${value_name},
	          (size_t) ${value_name}_size,
	          ${library_name_upper_case}_ENDIAN_LITTLE,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to copy ${type_description} from ${value_description}.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );
}

