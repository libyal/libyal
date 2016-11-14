/* Creates a new ${type_description} object
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_new(
           PyTypeObject *type_object,
           ${library_name}_${type_name}_t *${type_name},
           PyObject *parent_object )
{
	${python_module_name}_${type_name}_t *${python_module_name}_${type_name} = NULL;
	static char *function                                                    = "${python_module_name}_${type_name}_new";

	if( ${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_TypeError,
		 "%s: invalid ${type_description}.",
		 function );

		return( NULL );
	}
	${python_module_name}_${type_name} = PyObject_New(
	                                      struct ${python_module_name}_${type_name},
	                                      type_object );

	if( ${python_module_name}_${type_name} == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to initialize ${type_description}.",
		 function );

		goto on_error;
	}
	if( ${python_module_name}_${type_name}_init(
	     ${python_module_name}_${type_name} ) != 0 )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to initialize ${type_description}.",
		 function );

		goto on_error;
	}
	${python_module_name}_${type_name}->${type_name}  = ${type_name};
	${python_module_name}_${type_name}->parent_object = parent_object;

	Py_IncRef(
	 (PyObject *) ${python_module_name}_${type_name}->parent_object );

	return( (PyObject *) ${python_module_name}_${type_name} );

on_error:
	if( ${python_module_name}_${type_name} != NULL )
	{
		Py_DecRef(
		 (PyObject *) ${python_module_name}_${type_name} );
	}
	return( NULL );
}

