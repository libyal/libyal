#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_OpenDirectory(
               const wchar_t *path,
               DOKAN_FILE_INFO *file_info );
#endif

