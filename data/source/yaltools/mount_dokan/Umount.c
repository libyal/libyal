#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )

/* Unmounts the volume
 * Returns 0 if successful or an error code otherwise
 */
int __stdcall mount_dokan_Unmount(
               DOKAN_FILE_INFO *file_info ${tools_name_upper_case}_ATTRIBUTE_UNUSED )
{
	static char *function = "mount_dokan_Unmount";

	${tools_name_upper_case}_UNREFERENCED_PARAMETER( file_info )

#if defined( HAVE_DEBUG_OUTPUT )
	if( libcnotify_verbose != 0 )
	{
		libcnotify_printf(
		 "%s\n",
		 function );
	}
#endif
	return( 0 );
}

#endif /* ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 ) */

