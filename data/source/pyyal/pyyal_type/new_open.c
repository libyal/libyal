/* Creates a new ${type_description} object and opens it
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_new_open(
           PyObject *self ${python_module_name_upper_case}_ATTRIBUTE_UNUSED,
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *${python_module_name}_${type_name} = NULL;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( self )

	${python_module_name}_${type_name}_init(
	 (${python_module_name}_${type_name}_t *) ${python_module_name}_${type_name} );

	${python_module_name}_${type_name}_open(
	 (${python_module_name}_${type_name}_t *) ${python_module_name}_${type_name},
	 arguments,
	 keywords );

	return( ${python_module_name}_${type_name} );
}

/* Creates a new ${type_description} object and opens it using a file-like object
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_${type_name}_new_open_file_object(
           PyObject *self ${python_module_name_upper_case}_ATTRIBUTE_UNUSED,
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *${python_module_name}_${type_name} = NULL;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( self )

	${python_module_name}_${type_name}_init(
	 (${python_module_name}_${type_name}_t *) ${python_module_name}_${type_name} );

	${python_module_name}_${type_name}_open_file_object(
	 (${python_module_name}_${type_name}_t *) ${python_module_name}_${type_name},
	 arguments,
	 keywords );

	return( ${python_module_name}_${type_name} );
}

