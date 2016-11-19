/* Retrieves the root ${value_type_description} type object
 * Returns a Python type object if successful or NULL on error
 */
PyTypeObject *${python_module_name}_${type_name}_get_root_${value_type}_type_object(
               ${library_name}_${value_type}_t *root_${value_name} ${python_module_name_upper_case}_ATTRIBUTE_UNUSED )
{
	${python_module_name_upper_case}_UNREFERENCED_PARAMETER( root_${value_name} )

	return( &${python_module_name}_${value_type}_type_object );
}

