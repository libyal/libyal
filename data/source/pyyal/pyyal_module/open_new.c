/* Creates a new ${signature_type} object and opens it
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_open_new_${signature_type}(
           PyObject *self ${python_module_name_upper_case}_ATTRIBUTE_UNUSED,
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *${python_module_name}_${signature_type} = NULL;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( self )

	${python_module_name}_${signature_type}_init(
	 (${python_module_name}_${signature_type}_t *) ${python_module_name}_${signature_type} );

	${python_module_name}_${signature_type}_open(
	 (${python_module_name}_${signature_type}_t *) ${python_module_name}_${signature_type},
	 arguments,
	 keywords );

	return( ${python_module_name}_${signature_type} );
}

/* Creates a new ${signature_type} object and opens it using a file-like object
 * Returns a Python object if successful or NULL on error
 */
PyObject *${python_module_name}_open_new_${signature_type}_with_file_object(
           PyObject *self ${python_module_name_upper_case}_ATTRIBUTE_UNUSED,
           PyObject *arguments,
           PyObject *keywords )
{
	PyObject *${python_module_name}_${signature_type} = NULL;

	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( self )

	${python_module_name}_${signature_type}_init(
	 (${python_module_name}_${signature_type}_t *) ${python_module_name}_${signature_type} );

	${python_module_name}_${signature_type}_open_file_object(
	 (${python_module_name}_${signature_type}_t *) ${python_module_name}_${signature_type},
	 arguments,
	 keywords );

	return( ${python_module_name}_${signature_type} );
}

