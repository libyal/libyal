/* Test ${value_name} clone function
 * Returns 1 if successful or -1 on error
 */
int ${library_name_suffix}_test_${type_name}_${value_name}_clone_function(
     intptr_t **destination_${value_name} ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED,
     intptr_t *source_${value_name} ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED,
     libcerror_error_t **error ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED )
{
	${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( destination_${value_name} )
	${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( source_${value_name} )
	${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( error )

	return( 1 );
}

