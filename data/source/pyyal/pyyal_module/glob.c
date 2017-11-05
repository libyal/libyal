/* Globs filenames according to the Expert Witness Compression Format (EWF) segment file naming schema
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_glob(
           PyObject *self ${python_module_name_upper_case}_ATTRIBUTE_UNUSED,
           PyObject *arguments,
           PyObject *keywords )
{
	char **filenames_narrow          = NULL;
	libcerror_error_t *error         = NULL;
	PyObject *filename_string_object = NULL;
	PyObject *list_object            = NULL;
	PyObject *string_object          = NULL;
	static char *function            = "${python_module_name}_glob";
	static char *keyword_list[]      = { "filename", NULL };
	const char *errors               = NULL;
	const char *filename_narrow      = NULL;
	size_t filename_length           = 0;
	int filename_index               = 0;
	int number_of_filenames          = 0;
	int result                       = 0;

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	wchar_t **filenames_wide         = NULL;
	const wchar_t *filename_wide     = NULL;
#else
	PyObject *utf8_string_object     = NULL;
#endif

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( self )

	/* Note that PyArg_ParseTupleAndKeywords with "s" will force Unicode strings to be converted to narrow character string.
	 * On Windows the narrow character strings contains an extended ASCII string with a codepage. Hence we get a conversion
	 * exception. We cannot use "u" here either since that does not allow us to pass non Unicode string objects and
	 * Python (at least 2.7) does not seems to automatically upcast them.
	 */
	if( PyArg_ParseTupleAndKeywords(
	     arguments,
	     keywords,
	     "|O",
	     keyword_list,
	     &string_object ) == 0 )
	{
		return( NULL );
	}
	PyErr_Clear();

	result = PyObject_IsInstance(
	          string_object,
	          (PyObject *) &PyUnicode_Type );

	if( result == -1 )
	{
		${python_module_name}_error_fetch_and_raise(
	         PyExc_RuntimeError,
		 "%s: unable to determine if string object is of type unicode.",
		 function );

		goto on_error;
	}
	else if( result != 0 )
	{
		PyErr_Clear();

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		filename_wide = (wchar_t *) PyUnicode_AsUnicode(
		                             string_object );

		filename_length = wide_string_length(
		                   filename_wide );

		Py_BEGIN_ALLOW_THREADS

		result = ${library_name}_glob_wide(
			  filename_wide,
			  filename_length,
			  ${library_name_upper_case}_FORMAT_UNKNOWN,
			  &filenames_wide,
			  &number_of_filenames,
			  &error );

		Py_END_ALLOW_THREADS
#else
		utf8_string_object = PyUnicode_AsUTF8String(
		                      string_object );

		if( utf8_string_object == NULL )
		{
			${python_module_name}_error_fetch_and_raise(
			 PyExc_RuntimeError,
			 "%s: unable to convert unicode string to UTF-8.",
			 function );

			return( NULL );
		}
#if PY_MAJOR_VERSION >= 3
		filename_narrow = PyBytes_AsString(
				   utf8_string_object );
#else
		filename_narrow = PyString_AsString(
				   utf8_string_object );
#endif
		filename_length = narrow_string_length(
		                   filename_narrow );

		Py_BEGIN_ALLOW_THREADS

		result = ${library_name}_glob(
			  filename_narrow,
			  filename_length,
			  ${library_name_upper_case}_FORMAT_UNKNOWN,
			  &filenames_narrow,
			  &number_of_filenames,
			  &error );

		Py_END_ALLOW_THREADS

		Py_DecRef(
		 utf8_string_object );
#endif
		if( result != 1 )
		{
			${python_module_name}_error_raise(
			 error,
			 PyExc_IOError,
			 "%s: unable to glob filenames.",
			 function );

			libcerror_error_free(
			 &error );

			goto on_error;
		}
		list_object = PyList_New(
			       (Py_ssize_t) number_of_filenames );

		for( filename_index = 0;
		     filename_index < number_of_filenames;
		     filename_index++ )
		{
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
			filename_length = wide_string_length(
					   filenames_wide[ filename_index ] );

			filename_string_object = PyUnicode_FromWideChar(
						  filenames_wide[ filename_index ],
						  filename_length );
#else
			filename_length = narrow_string_length(
			                   filenames_narrow[ filename_index ] );

			/* Pass the string length to PyUnicode_DecodeUTF8
			 * otherwise it makes the end of string character is part
			 * of the string
			 */
			filename_string_object = PyUnicode_DecodeUTF8(
			                          filenames_narrow[ filename_index ],
			                          filename_length,
			                          errors );
#endif
			if( filename_string_object == NULL )
			{
				PyErr_Format(
				 PyExc_IOError,
				 "%s: unable to convert filename: %d into Unicode.",
				 function,
				 filename_index );

				goto on_error;
			}
			if( PyList_SetItem(
			     list_object,
			     (Py_ssize_t) filename_index,
			     filename_string_object ) != 0 )
			{
				PyErr_Format(
				 PyExc_MemoryError,
				 "%s: unable to set filename: %d in list.",
				 function,
				 filename_index );

				goto on_error;
			}
			filename_string_object = NULL;
		}
		Py_BEGIN_ALLOW_THREADS

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
		result = ${library_name}_glob_wide_free(
			  filenames_wide,
			  number_of_filenames,
			  &error );
#else
		result = ${library_name}_glob_free(
			  filenames_narrow,
			  number_of_filenames,
			  &error );
#endif

		Py_END_ALLOW_THREADS

		if( result != 1 )
		{
			${python_module_name}_error_raise(
			 error,
			 PyExc_MemoryError,
			 "%s: unable to free globbed filenames.",
			 function );

			libcerror_error_free(
			 &error );

			goto on_error;
		}
		return( list_object );
	}
	PyErr_Clear();

#if PY_MAJOR_VERSION >= 3
	result = PyObject_IsInstance(
		  string_object,
		  (PyObject *) &PyBytes_Type );
#else
	result = PyObject_IsInstance(
		  string_object,
		  (PyObject *) &PyString_Type );
#endif
	if( result == -1 )
	{
		${python_module_name}_error_fetch_and_raise(
	         PyExc_RuntimeError,
		 "%s: unable to determine if string object is of type string.",
		 function );

		goto on_error;
	}
	else if( result != 0 )
	{
		PyErr_Clear();

#if PY_MAJOR_VERSION >= 3
		filename_narrow = PyBytes_AsString(
				   string_object );
#else
		filename_narrow = PyString_AsString(
				   string_object );
#endif
		filename_length = narrow_string_length(
		                   filename_narrow );

		Py_BEGIN_ALLOW_THREADS

		result = ${library_name}_glob(
			  filename_narrow,
			  filename_length,
			  ${library_name_upper_case}_FORMAT_UNKNOWN,
			  &filenames_narrow,
			  &number_of_filenames,
			  &error );

		Py_END_ALLOW_THREADS

		if( result != 1 )
		{
			${python_module_name}_error_raise(
			 error,
			 PyExc_IOError,
			 "%s: unable to glob filenames.",
			 function );

			libcerror_error_free(
			 &error );

			goto on_error;
		}
		list_object = PyList_New(
			       (Py_ssize_t) number_of_filenames );

		for( filename_index = 0;
		     filename_index < number_of_filenames;
		     filename_index++ )
		{
			filename_length = narrow_string_length(
					   filenames_narrow[ filename_index ] );

			filename_string_object = PyUnicode_Decode(
						  filenames_narrow[ filename_index ],
						  filename_length,
						  PyUnicode_GetDefaultEncoding(),
						  errors );

			if( filename_string_object == NULL )
			{
				PyErr_Format(
				 PyExc_IOError,
				 "%s: unable to convert filename: %d into Unicode.",
				 function,
				 filename_index );

				goto on_error;
			}
			if( PyList_SetItem(
			     list_object,
			     (Py_ssize_t) filename_index,
			     filename_string_object ) != 0 )
			{
				PyErr_Format(
				 PyExc_MemoryError,
				 "%s: unable to set filename: %d in list.",
				 function,
				 filename_index );

				goto on_error;
			}
			filename_string_object = NULL;
		}
		Py_BEGIN_ALLOW_THREADS

		result = ${library_name}_glob_free(
			  filenames_narrow,
			  number_of_filenames,
			  &error );

		Py_END_ALLOW_THREADS

		if( result != 1 )
		{
			${python_module_name}_error_raise(
			 error,
			 PyExc_MemoryError,
			 "%s: unable to free globbed filenames.",
			 function );

			libcerror_error_free(
			 &error );

			goto on_error;
		}
		return( list_object );
	}
	PyErr_Format(
	 PyExc_TypeError,
	 "%s: unsupported string object type.",
	 function );

on_error:
	if( filename_string_object != NULL )
	{
		Py_DecRef(
		 filename_string_object );
	}
	if( list_object != NULL )
	{
		Py_DecRef(
		 list_object );
	}
	if( filenames_narrow != NULL )
	{
		Py_BEGIN_ALLOW_THREADS

		${library_name}_glob_free(
		 filenames_narrow,
		 number_of_filenames,
		 NULL );

		Py_END_ALLOW_THREADS
	}
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
	if( filenames_wide != NULL )
	{
		Py_BEGIN_ALLOW_THREADS

		${library_name}_glob_wide_free(
		 filenames_wide,
		 number_of_filenames,
		 NULL );

		Py_END_ALLOW_THREADS
	}
#endif
	return( NULL );
}

