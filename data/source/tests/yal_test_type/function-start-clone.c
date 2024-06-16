/* Tests the ${library_name}_${type_name}_${function_name} function
 * Returns 1 if successful or 0 if not
 */
int ${library_name_suffix}_test_${type_name}_${function_name}(
     void )
{
${function_variables}

#if defined( HAVE_${library_name_suffix:upper_case}_TEST_MEMORY )
	int number_of_malloc_fail_tests              = 1;
	int test_number                              = 0;

#if defined( OPTIMIZATION_DISABLED )
	int number_of_memcpy_fail_tests              = 1;
#endif
#endif /* defined( HAVE_${library_name_suffix:upper_case}_TEST_MEMORY ) */

