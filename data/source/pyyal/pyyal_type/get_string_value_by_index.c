/* Retrieves a specific ${value_description} by index
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_${value_name}_by_index(
           PyObject *${python_module_name}_${type_name},
           int ${value_name}_index )
{
	libcerror_error_t *error = NULL;
	PyObject *string_object  = NULL;
	uint8_t *utf8_string     = NULL;
	const char *errors       = NULL;
	static char *function    = "${python_module_name}_${type_name}_get_${value_name}_by_index";
	size_t utf8_string_size  = 0;
	int result               = 0;

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_utf8_${value_name}_size(
	          ( (${python_module_name}_${type_name}_t *) ${python_module_name}_${type_name} )->${type_name},
	          ${value_name}_index,
	          &utf8_string_size,
	          &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to determine size of ${value_description}: %d as UTF-8 string.",
		 function,
		 ${value_name}_index );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	else if( ( result == 0 )
	      || ( utf8_string_size == 0 ) )
	{
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	utf8_string = (uint8_t *) PyMem_Malloc(
	                           sizeof( uint8_t ) * utf8_string_size );

	if( utf8_string == NULL )
	{
		PyErr_Format(
		 PyExc_IOError,
		 "%s: unable to create UTF-8 string.",
		 function );

		goto on_error;
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_utf8_${value_name}(
		  ( (${python_module_name}_${type_name}_t *) ${python_module_name}_${type_name} )->${type_name},
		  ${value_name}_index,
		  utf8_string,
		  utf8_string_size,
		  &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve ${value_description}: %d as UTF-8 string.",
		 function,
		 ${value_name}_index );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	/* Pass the string length to PyUnicode_DecodeUTF8 otherwise it makes
	 * the end of string character is part of the string
	 */
	string_object = PyUnicode_DecodeUTF8(
	                 (char *) utf8_string,
	                 (Py_ssize_t) utf8_string_size - 1,
	                 errors );

	if( string_object == NULL )
	{
		PyErr_Format(
		 PyExc_IOError,
		 "%s: unable to convert UTF-8 string into Unicode object.",
		 function );

		goto on_error;
	}
	PyMem_Free(
	 utf8_string );

	return( string_object );

on_error:
	if( utf8_string != NULL )
	{
		PyMem_Free(
		 utf8_string );
	}
	return( NULL );
}

/* Retrieves a specific ${value_description}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_${value_name}(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *string_object     = NULL;
	static char *keyword_list[] = { "${value_name}_index", NULL };
	int ${value_name}_index     = 0;

	if( PyArg_ParseTupleAndKeywords(
	     arguments,
	     keywords,
	     "i",
	     keyword_list,
	     &${value_name}_index ) == 0 )
	{
		return( NULL );
	}
	string_object = ${python_module_name}_${type_name}_get_${value_name}_by_index(
	                 (PyObject *) ${python_module_name}_${type_name},
	                 ${value_name}_index );

	return( string_object );
}

/* Retrieves a sequence and iterator object for the ${value_description}s
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_${value_name}s(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *sequence_object    = NULL;
	libcerror_error_t *error     = NULL;
	static char *function        = "${python_module_name}_${type_name}_get_${value_name}s";
	int number_of_${value_name}s = 0;
	int result                   = 0;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( arguments )

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_get_number_of_${value_name}s(
	          ${python_module_name}_${type_name}->${type_name},
	          &number_of_${value_name}s,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve number of ${value_description}s.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	sequence_object = ${python_module_name}_${value_name}s_new(
	                   (PyObject *) ${python_module_name}_${type_name},
	                   &${python_module_name}_${type_name}_get_${value_name}_by_index,
	                   number_of_${value_name}s );

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

