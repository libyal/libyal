/* Sets the ${value_description}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_set_parent(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments,
           PyObject *keywords )
{
	libcerror_error_t *error                            = NULL;
	${python_module_name}_${type_name}_t *${value_name} = NULL;
	static char *function                               = "${python_module_name}_${type_name}_set_parent";
	static char *keyword_list[]                         = { "${value_name}", NULL };
	int result                                          = 0;

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
	     "O!",
	     keyword_list,
	     &${python_module_name}_${type_name}_type_object,
	     &${value_name} ) == 0)
	{
		return( NULL );
	}
	Py_BEGIN_ALLOW_THREADS

	result = ${library_name}_${type_name}_set_${value_name}(
	          ${python_module_name}_${type_name}->${type_name},
	          ${value_name}->${type_name},
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
	${python_module_name}_${type_name}->parent_${type_name}_object = ${value_name};

	Py_IncRef(
	 ${python_module_name}_${type_name}->parent_${type_name}_object );

	Py_IncRef(
	 Py_None );

	return( Py_None );
}

