/* Creates a new ${signature_type} object and opens it
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_open_new_${signature_type}(
           PyObject *self ${python_module_name_upper_case}_ATTRIBUTE_UNUSED,
           PyObject *arguments,
           PyObject *keywords )
{
	${python_module_name}_${signature_type}_t *${python_module_name}_${signature_type} = NULL;
	static char *function                                                              = "${python_module_name}_open_new_${signature_type}";

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( self )

	/* PyObject_New does not invoke tp_init
	 */
	${python_module_name}_${signature_type} = PyObject_New(
	                                           struct ${python_module_name}_${signature_type},
	                                           &${python_module_name}_${signature_type}_type_object );

	if( ${python_module_name}_${signature_type} == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create ${signature_type}.",
		 function );

		goto on_error;
	}
	if( ${python_module_name}_${signature_type}_init(
	     ${python_module_name}_${signature_type} ) != 0 )
	{
		goto on_error;
	}
	if( ${python_module_name}_${signature_type}_open(
	     ${python_module_name}_${signature_type},
	     arguments,
	     keywords ) == NULL )
	{
		goto on_error;
	}
	return( (PyObject *) ${python_module_name}_${signature_type} );

on_error:
	if( ${python_module_name}_${signature_type} != NULL )
	{
		Py_DecRef(
		 (PyObject *) ${python_module_name}_${signature_type} );
	}
	return( NULL );
}

/* Creates a new ${signature_type} object and opens it using a file-like object
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_open_new_${signature_type}_with_file_object(
           PyObject *self ${python_module_name_upper_case}_ATTRIBUTE_UNUSED,
           PyObject *arguments,
           PyObject *keywords )
{
	${python_module_name}_${signature_type}_t *${python_module_name}_${signature_type} = NULL;
	static char *function                                                              = "${python_module_name}_open_new_${signature_type}_with_file_object";

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( self )

	/* PyObject_New does not invoke tp_init
	 */
	${python_module_name}_${signature_type} = PyObject_New(
	                                           struct ${python_module_name}_${signature_type},
	                                           &${python_module_name}_${signature_type}_type_object );

	if( ${python_module_name}_${signature_type} == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create ${signature_type}.",
		 function );

		goto on_error;
	}
	if( ${python_module_name}_${signature_type}_init(
	     ${python_module_name}_${signature_type} ) != 0 )
	{
		goto on_error;
	}
	if( ${python_module_name}_${signature_type}_open_file_object(
	     ${python_module_name}_${signature_type},
	     arguments,
	     keywords ) == NULL )
	{
		goto on_error;
	}
	return( (PyObject *) ${python_module_name}_${signature_type} );

on_error:
	if( ${python_module_name}_${signature_type} != NULL )
	{
		Py_DecRef(
		 (PyObject *) ${python_module_name}_${signature_type} );
	}
	return( NULL );
}

