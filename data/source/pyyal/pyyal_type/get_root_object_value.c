/* Retrieves the root ${value_description} type object
 * Returns a Python type object if successful or NULL on error
 */
PyTypeObject *${python_module_name}_${type_name}_get_root_${value_name}_type_object(
               ${library_name}_${value_type}_t *root_${value_name} ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( root_${value_name} )

	return( &${python_module_name}_${value_type}_type_object );
}

/* Retrieves the root ${value_description}
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_get_root_${value_name}(
           ${python_module_name}_${type_name}_t *${python_module_name}_${type_name},
           PyObject *arguments ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	PyObject *${value_name}_object                      = NULL;
	PyTypeObject *type_object                           = NULL;
	libcerror_error_t *error                            = NULL;
	${library_name}_${value_type}_t *root_${value_name} = NULL;
	static char *function                               = "${python_module_name}_${type_name}_get_root_${value_name}";
	int result                                          = 0;

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

	result = ${library_name}_${type_name}_get_root_${value_name}(
	          ${python_module_name}_${type_name}->${type_name},
	          &root_${value_name},
	          &error );

	Py_END_ALLOW_THREADS

	if( result == -1 )
	{
		${python_module_name}_error_raise(
		 error,
		 PyExc_IOError,
		 "%s: unable to retrieve root ${value_description}.",
		 function );

		libcerror_error_free(
		 &error );

		goto on_error;
	}
	else if( result == 0 )
	{
		Py_IncRef(
		 Py_None );

		return( Py_None );
	}
	type_object = ${python_module_name}_${type_name}_get_root_${value_name}_type_object(
	               root_${value_name} );

	if( type_object == NULL )
	{
		PyErr_Format(
		 PyExc_IOError,
		 "%s: unable to retrieve root ${value_description} type object.",
		 function );

		goto on_error;
	}
	${value_name}_object = ${python_module_name}_${value_type}_new(
	                        type_object,
	                        root_${value_name},
	                        (PyObject *) ${python_module_name}_${type_name} );

	if( ${value_name}_object == NULL )
	{
		PyErr_Format(
		 PyExc_MemoryError,
		 "%s: unable to create ${value_description} object.",
		 function );

		goto on_error;
	}
	return( ${value_name}_object );

on_error:
	if( root_${value_name} != NULL )
	{
		${library_name}_${value_type}_free(
		 &root_${value_name},
		 NULL );
	}
	return( NULL );
}

