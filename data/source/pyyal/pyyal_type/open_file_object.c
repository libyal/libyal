/* Opens a ${type_description} using a file-like object
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_open_file_object(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *file_object       = NULL;
	libcerror_error_t *error    = NULL;
	char *mode                  = NULL;
	static char *keyword_list[] = { "file_object", "mode", NULL };
	static char *function       = "${python_module_name}_${type_name}_open_file_object";
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
	     "O|s",
	     keyword_list,
	     &file_object,
	     &mode ) == 0 )
	{
		return( NULL );
	}
	if( ( mode != NULL )
	 && ( mode[ 0 ] != 'r' ) )
	{
		PyErr_Format(
		 PyExc_ValueError,
		 "%s: unsupported mode: %s.",
		 function,
		 mode );

		return( NULL );
	}
	if( ${python_module_name}_${type_name}->file_io_handle != NULL )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: invalid ${type_description} - file IO handle already set.",
		 function );

		goto on_error;
	}
	if( ${python_module_name}_file_object_initialize(
	     &( ${python_module_name}_${type_name}->file_io_handle ),
	     file_object,
	     &error ) != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_MemoryError,
		 "%s: unable to initialize file IO handle.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_open_file_io_handle(
	          ${python_module_name}_${type_name}->${type_name},
	          ${python_module_name}_${type_name}->file_io_handle,
	          ${library_name_upper_case}_OPEN_READ,
	          &error );

	Py_END_ALLOW_THREADS

	if( result != 1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to open ${type_description}.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );

on_error:
	if( ${python_module_name}_${type_name}->file_io_handle != NULL )
	{
		libbfio_handle_free(
		 &( ${python_module_name}_${type_name}->file_io_handle ),
		 NULL );
	}
	return( NULL );
}

