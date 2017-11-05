/* The main program
 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
int wmain(
     int argc ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED,
     wchar_t * const argv[] ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED )
#else
int main(
     int argc ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED,
     char * const argv[] ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED )
#endif
{
	libcerror_error_t *error                     = NULL;
	${library_name}_${type_name}_t *${type_name} = NULL;
	int result                                   = 0;

	${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( argc )
	${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( argv )

