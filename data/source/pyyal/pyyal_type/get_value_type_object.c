/* Retrieves the ${value_description} type object
 * Returns a Python type object if successful or NULL on error
 */
PyTypeObject *${python_module_name}_${type_name}_get_${value_name}_type_object(
               ${library_name}_${value_name}_t *${value_name} ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( ${value_name} )

	return( &${python_module_name}_${value_name}_type_object );
}

