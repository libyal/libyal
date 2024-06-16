/* Signal handler for ${mount_tool_name}
 */
void ${mount_tool_name}_signal_handler(
      ${tools_name}_signal_t signal ${tools_name:upper_case}_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "${mount_tool_name}_signal_handler";

	${tools_name:upper_case}_UNREFERENCED_PARAMETER( signal )

	${mount_tool_name}_abort = 1;

	if( ${mount_tool_name}_mount_handle != NULL )
	{
		if( mount_handle_signal_abort(
		     ${mount_tool_name}_mount_handle,
		     &error ) != 1 )
		{
			libcnotify_printf(
			 "%s: unable to signal mount handle to abort.\n",
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

