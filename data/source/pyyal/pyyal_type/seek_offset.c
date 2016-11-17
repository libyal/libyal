/* Seeks a certain offset
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_seek_offset(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	libcerror_error_t *error    = NULL;
	static char *function       = "${python_module_name}_${type_name}_seek_offset";
	static char *keyword_list[] = { "offset", "whence", NULL };
	off64_t offset              = 0;
	int whence                  = 0;

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
	     "L|i",
	     keyword_list,
	     &offset,
	     &whence ) == 0 )
	{
		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	offset = ${library_name}_${type_name}_seek_offset(
	          ${python_module_name}_${type_name}->${type_name},
	          offset,
	          whence,
	          &error );

	Py_END_ALLOW_THREADS

 	if( offset == -1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to seek offset.",
		 function );

		libcerror_error_free(
		 &error );

		return( NULL );
	}
	Py_IncRef(
	 Py_None );

	return( Py_None );
}

