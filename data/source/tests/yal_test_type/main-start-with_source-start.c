/* The main program
 */
#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
int wmain(
     int argc,
     wchar_t * const argv[] )
#else
int main(
     int argc,
     char * const argv[] )
#endif
{
	libbfio_${bfio_type}_t *file_io_${bfio_type} = NULL;
	libcerror_error_t *error                     = NULL;
	${library_name}_${type_name}_t *${type_name} = NULL;
${test_options_variable_declarations}
	system_integer_t option                      = 0;
	size_t string_length                         = 0;
	int result                                   = 0;

	while( ( option = ${library_name_suffix}_test_getopt(
	                   argc,
	                   argv,
	                   _SYSTEM_STRING( "${test_getopt_string}" ) ) ) != (system_integer_t) -1 )
	{
		switch( option )
		{
			case (system_integer_t) '?':
			default:
				fprintf(
				 stderr,
				 "Invalid argument: %" PRIs_SYSTEM ".\n",
				 argv[ optind - 1 ] );

				return( EXIT_FAILURE );
