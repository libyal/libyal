/* Creates a new ${type_name} object
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_new(
           void )
{
	${python_module_name}_${type_name}_t *${python_module_name}_${type_name} = NULL;
	static char *function                                                    = "${python_module_name}_${type_name}_new";

	${python_module_name}_${type_name} = PyObject_New(
	                                      struct ${python_module_name}_${type_name},
	                                      &${python_module_name}_${type_name}_type_object );

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to initialize ${type_name}.",
		 function );

		goto on_error;
	}
	if( ${python_module_name}_${type_name}_init(
	     ${python_module_name}_${type_name} ) != 0 )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to initialize ${type_name}.",
		 function );

		goto on_error;
	}
	return( (PyObject *) ${python_module_name}_${type_name} );

on_error:
	if( ${python_module_name}_${type_name} != NULL )
	{
		Py_DecRef(
		 (PyObject *) ${python_module_name}_${type_name} );
	}
	return( NULL );
}

