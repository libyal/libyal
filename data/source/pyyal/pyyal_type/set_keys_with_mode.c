/* Sets the keys
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_set_keys(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	libcerror_error_t *error          = NULL;
	PyObject *key_string_object       = NULL;
	PyObject *tweak_key_string_object = NULL;
	static char *function             = "${python_module_name}_${type_name}_set_key";
	static char *keyword_list[]       = { "mode", "key", "tweak_key", NULL };
	char *key_data                    = NULL;
	char *tweak_key_data              = NULL;
        Py_ssize_t key_data_size          = 0;
        Py_ssize_t tweak_key_data_size    = 0;
	int mode                          = 0;
	int result                        = 0;

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
	     "iOO",
	     keyword_list,
	     &mode,
	     &key_string_object,
	     &tweak_key_string_object ) == 0 )
	{
		return( NULL );
	}
#if PY_MAJOR_VERSION >= 3
	key_data = PyBytes_AsString(
	            key_string_object );

	key_data_size = PyBytes_Size(
	                 key_string_object );
#else
	key_data = PyString_AsString(
	            key_string_object );

	key_data_size = PyString_Size(
	                 key_string_object );
#endif
	if( ( key_data_size < 0 )
	 || ( key_data_size > (Py_ssize_t) ( SSIZE_MAX / 8 ) ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid key data size value out of bounds.",
		 function );

		return( NULL );
	}
#if PY_MAJOR_VERSION >= 3
	tweak_key_data = PyBytes_AsString(
	                  tweak_key_string_object );

	tweak_key_data_size = PyBytes_Size(
	                       tweak_key_string_object );
#else
	tweak_key_data = PyString_AsString(
	                  tweak_key_string_object );

	tweak_key_data_size = PyString_Size(
	                       tweak_key_string_object );
#endif
	if( ( tweak_key_data_size < 0 )
	 || ( tweak_key_data_size > (Py_ssize_t) ( SSIZE_MAX / 8 ) ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid tweak key data size value out of bounds.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_set_keys(
	          ${python_module_name}_${type_name}->${type_name},
	          mode,
	          (uint8_t *) key_data,
	          (size_t) ( key_data_size * 8 ),
	          (uint8_t *) tweak_key_data,
	          (size_t) ( tweak_key_data_size * 8 ),
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to set keys.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );
}

