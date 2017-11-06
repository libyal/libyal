/* Signal handler for ${info_tool_name}
 */
void ${info_tool_name}_signal_handler(
      ${tools_name}_signal_t signal ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${info_tool_name}_signal_handler";

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( signal )

	${info_tool_name}_abort = 1;

	if( ${info_tool_name}_info_handle != NULL )
	{
		if( info_handle_signal_abort(
		     ${info_tool_name}_info_handle,
		     &error ) != 1 )
		{
			libcnotify_printf(
			 "%s: unable to signal info handle to abort.\n",
			 function );

			libcnotify_print_error_backtrace(
			 error );
			libcerror_error_free(
			 &error );
		}
	}
	/* Force stdin to close otherwise any function reading it will remain blocked
	 */
#if defined( WINAPI ) && !defined( __CYGWIN__ )
	if( _close(
	     0 ) != 0 )
#else
	if( close(
	     0 ) != 0 )
#endif
	{
		libcnotify_printf(
		 "%s: unable to close stdin.\n",
		 function );
	}
}

