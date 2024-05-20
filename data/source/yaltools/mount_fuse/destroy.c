/* Cleans up when fuse is done
 */
void mount_fuse_destroy(
      void *private_data ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
{
	libcerror_error_t *error = NULL;
	static char *function    = "mount_fuse_destroy";

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( private_data )

#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
		libcnotify_printf(
		 "%s\n",
		 function );
	}
#endif
	if( ${mount_tool_name}_mount_handle != NULL )
	{
		if( mount_handle_free(
		     &${mount_tool_name}_mount_handle,
		     &error ) != 1 )
		{
			libcerror_error_set(
			 &error,
			 LIBCERROR_ERROR_DOMAIN_RUNTIME,
			 LIBCERROR_RUNTIME_ERROR_FINALIZE_FAILED,
			 "%s: unable to free mount handle.",
			 function );

			goto on_error;
		}
	}
	return;

on_error:
	if( error != NULL )
	{
		libcnotify_print_error_backtrace(
		 error );
		libcerror_error_free(
		 &error );
	}
	return;
}

