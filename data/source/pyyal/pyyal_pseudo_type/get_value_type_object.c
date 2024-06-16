/* Retrieves the ${value_type_description} type object
 * Returns a Python type object if successful or NULL on error
 */
PyTypeObject *${python_module_name}_${type_name}_get_${value_type}_type_object(
               ${library_name}_${value_type}_t *${value_type} ${python_module_name:upper_case}_ATTRIBUTE_UNUSED )
{
	${python_module_name:upper_case}_UNREFERENCED_PARAMETER( ${value_type} )

	return( &${python_module_name}_${value_type}_type_object );
}

