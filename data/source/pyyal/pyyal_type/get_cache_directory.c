/* Retrieves a specific cache directory by index
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_cache_directory_by_index(
           PyObject *${python_module_name}_${type_name},
           int cache_directory_index )
{
	char string[ 9 ];

	PyObject *string_object  = NULL;
	libcerror_error_t *error = NULL;
	static char *function    = "${python_module_name}_${type_name}_get_cache_directory_by_index";
	int result               = 0;

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_cache_directory_name(
	          ( (${python_module_name}_${type_name}_t *) ${python_module_name}_${type_name} )->${type_name},
	          cache_directory_index,
	          string,
	          9,
	          &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve cache directory name: %d.",
		 function,
		 cache_directory_index );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	else if( result == 0 )
	{
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	/* Assumed that the directory name contains only basic ASCII characters
	 */
#if PY_MAJOR_VERSION >= 3
	string_object = PyBytes_FromString(
	                 string );
#else
	string_object = PyString_FromString(
	                 string );
#endif
	if( string_object == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to convert cache directory name string into string object.",
		 function );

		return( NULL );
	}
	return( string_object );
}

/* Retrieves a specific cache directory
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_cache_directory(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *string_object     = NULL;
	static char *keyword_list[] = { "cache_directory_index", NULL };
	int cache_directory_index   = 0;

	if( PyArg_ParseTupleAndKeywords(
	     arguments,
	     keywords,
	     "i",
	     keyword_list,
	     &cache_directory_index ) == 0 )
	{
		return( NULL );
	}
	string_object = ${python_module_name}_${type_name}_get_cache_directory_by_index(
	                 (PyObject *) ${python_module_name}_${type_name},
	                 cache_directory_index );

	return( string_object );
}

/* Retrieves a sequence and iterator object for the cache directories
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_cache_directories(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *sequence_object       = NULL;
	libcerror_error_t *error        = NULL;
	static char *function           = "${python_module_name}_${type_name}_get_cache_directories";
	int number_of_cache_directories = 0;
	int result                      = 0;

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

	result = ${library_name}_${type_name}_get_number_of_cache_directories(
	          ${python_module_name}_${type_name}->${type_name},
	          &number_of_cache_directories,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve number of cache directories.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	sequence_object = ${python_module_name}_cache_directories_new(
	                   (PyObject *) ${python_module_name}_${type_name},
	                   &${python_module_name}_${type_name}_get_cache_directory_by_index,
	                   number_of_cache_directories );

	if( sequence_object == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create sequence object.",
		 function );

		return( NULL );
	}
	return( sequence_object );
}

