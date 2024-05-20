#elif defined( HAVE_LIBDOKAN )
	if( memory_set(
	     &${mount_tool_name}_dokan_operations,
	     0,
	     sizeof( DOKAN_OPERATIONS ) ) == NULL )
	{
		fprintf(
		 stderr,
		 "Unable to clear dokan operations.\n" );

		goto on_error;
	}
	if( memory_set(
	     &${mount_tool_name}_dokan_options,
	     0,
	     sizeof( DOKAN_OPTIONS ) ) == NULL )
	{
		fprintf(
		 stderr,
		 "Unable to clear dokan options.\n" );

		goto on_error;
	}
	${mount_tool_name}_dokan_options.Version    = DOKAN_VERSION;
	${mount_tool_name}_dokan_options.MountPoint = mount_point;

#if DOKAN_MINIMUM_COMPATIBLE_VERSION >= 200
	${mount_tool_name}_dokan_options.SingleThread = TRUE;
#else
	${mount_tool_name}_dokan_options.ThreadCount  = 0;
#endif
	if( verbose != 0 )
	{
		${mount_tool_name}_dokan_options.Options |= DOKAN_OPTION_STDERR;
#if defined( HAVE_DEBUG_OUTPUT )
		${mount_tool_name}_dokan_options.Options |= DOKAN_OPTION_DEBUG;
#endif
	}
/* This will only affect the drive properties
	${mount_tool_name}_dokan_options.Options |= DOKAN_OPTION_REMOVABLE;
*/

#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
	${mount_tool_name}_dokan_options.Options |= DOKAN_OPTION_KEEP_ALIVE;

	${mount_tool_name}_dokan_operations.CreateFile           = &mount_dokan_CreateFile;
	${mount_tool_name}_dokan_operations.OpenDirectory        = &mount_dokan_OpenDirectory;
	${mount_tool_name}_dokan_operations.CreateDirectory      = NULL;
	${mount_tool_name}_dokan_operations.Cleanup              = NULL;
	${mount_tool_name}_dokan_operations.CloseFile            = &mount_dokan_CloseFile;
	${mount_tool_name}_dokan_operations.ReadFile             = &mount_dokan_ReadFile;
	${mount_tool_name}_dokan_operations.WriteFile            = NULL;
	${mount_tool_name}_dokan_operations.FlushFileBuffers     = NULL;
	${mount_tool_name}_dokan_operations.GetFileInformation   = &mount_dokan_GetFileInformation;
	${mount_tool_name}_dokan_operations.FindFiles            = &mount_dokan_FindFiles;
	${mount_tool_name}_dokan_operations.FindFilesWithPattern = NULL;
	${mount_tool_name}_dokan_operations.SetFileAttributes    = NULL;
	${mount_tool_name}_dokan_operations.SetFileTime          = NULL;
	${mount_tool_name}_dokan_operations.DeleteFile           = NULL;
	${mount_tool_name}_dokan_operations.DeleteDirectory      = NULL;
	${mount_tool_name}_dokan_operations.MoveFile             = NULL;
	${mount_tool_name}_dokan_operations.SetEndOfFile         = NULL;
	${mount_tool_name}_dokan_operations.SetAllocationSize    = NULL;
	${mount_tool_name}_dokan_operations.LockFile             = NULL;
	${mount_tool_name}_dokan_operations.UnlockFile           = NULL;
	${mount_tool_name}_dokan_operations.GetFileSecurity      = NULL;
	${mount_tool_name}_dokan_operations.SetFileSecurity      = NULL;
	${mount_tool_name}_dokan_operations.GetDiskFreeSpace     = NULL;
	${mount_tool_name}_dokan_operations.GetVolumeInformation = &mount_dokan_GetVolumeInformation;
	${mount_tool_name}_dokan_operations.Unmount              = &mount_dokan_Unmount;

#else
	${mount_tool_name}_dokan_operations.ZwCreateFile         = &mount_dokan_ZwCreateFile;
	${mount_tool_name}_dokan_operations.Cleanup              = NULL;
	${mount_tool_name}_dokan_operations.CloseFile            = &mount_dokan_CloseFile;
	${mount_tool_name}_dokan_operations.ReadFile             = &mount_dokan_ReadFile;
	${mount_tool_name}_dokan_operations.WriteFile            = NULL;
	${mount_tool_name}_dokan_operations.FlushFileBuffers     = NULL;
	${mount_tool_name}_dokan_operations.GetFileInformation   = &mount_dokan_GetFileInformation;
	${mount_tool_name}_dokan_operations.FindFiles            = &mount_dokan_FindFiles;
	${mount_tool_name}_dokan_operations.FindFilesWithPattern = NULL;
	${mount_tool_name}_dokan_operations.SetFileAttributes    = NULL;
	${mount_tool_name}_dokan_operations.SetFileTime          = NULL;
	${mount_tool_name}_dokan_operations.DeleteFile           = NULL;
	${mount_tool_name}_dokan_operations.DeleteDirectory      = NULL;
	${mount_tool_name}_dokan_operations.MoveFile             = NULL;
	${mount_tool_name}_dokan_operations.SetEndOfFile         = NULL;
	${mount_tool_name}_dokan_operations.SetAllocationSize    = NULL;
	${mount_tool_name}_dokan_operations.LockFile             = NULL;
	${mount_tool_name}_dokan_operations.UnlockFile           = NULL;
	${mount_tool_name}_dokan_operations.GetFileSecurity      = NULL;
	${mount_tool_name}_dokan_operations.SetFileSecurity      = NULL;
	${mount_tool_name}_dokan_operations.GetDiskFreeSpace     = NULL;
	${mount_tool_name}_dokan_operations.GetVolumeInformation = &mount_dokan_GetVolumeInformation;
	${mount_tool_name}_dokan_operations.Unmounted            = NULL;
	${mount_tool_name}_dokan_operations.FindStreams          = NULL;
	${mount_tool_name}_dokan_operations.Mounted              = NULL;

#endif /* ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 ) */

#if DOKAN_MINIMUM_COMPATIBLE_VERSION >= 200
	DokanInit();
#endif
	result = DokanMain(
	          &${mount_tool_name}_dokan_options,
	          &${mount_tool_name}_dokan_operations );

#if DOKAN_MINIMUM_COMPATIBLE_VERSION >= 200
	DokanShutdown();
#endif
	switch( result )
	{
		case DOKAN_SUCCESS:
			break;

		case DOKAN_ERROR:
			fprintf(
			 stderr,
			 "Unable to run dokan main: generic error\n" );
			break;

		case DOKAN_DRIVE_LETTER_ERROR:
			fprintf(
			 stderr,
			 "Unable to run dokan main: bad drive letter\n" );
			break;

		case DOKAN_DRIVER_INSTALL_ERROR:
			fprintf(
			 stderr,
			 "Unable to run dokan main: unable to load driver\n" );
			break;

		case DOKAN_START_ERROR:
			fprintf(
			 stderr,
			 "Unable to run dokan main: driver error\n" );
			break;

		case DOKAN_MOUNT_ERROR:
			fprintf(
			 stderr,
			 "Unable to run dokan main: unable to assign drive letter\n" );
			break;

		case DOKAN_MOUNT_POINT_ERROR:
			fprintf(
			 stderr,
			 "Unable to run dokan main: mount point error\n" );
			break;

		default:
			fprintf(
			 stderr,
			 "Unable to run dokan main: unknown error: %d\n",
			 result );
			break;
	}
	return( EXIT_SUCCESS );

