/* Test ${value_name} free function
 * Returns 1 if successful or -1 on error
 */
int ${library_name_suffix}_test_${type_name}_${value_name}_free_function(
     intptr_t **${value_name} ${library_name_suffix:upper_case}_TEST_ATTRIBUTE_UNUSED,
     libcerror_error_t **error ${library_name_suffix:upper_case}_TEST_ATTRIBUTE_UNUSED )
{
	${library_name_suffix:upper_case}_TEST_UNREFERENCED_PARAMETER( ${value_name} )
	${library_name_suffix:upper_case}_TEST_UNREFERENCED_PARAMETER( error )

	return( 1 );
}

