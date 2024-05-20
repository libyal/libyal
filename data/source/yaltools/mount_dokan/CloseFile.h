#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_CloseFile(
               const wchar_t *path,
               DOKAN_FILE_INFO *file_info );
#else
NTSTATUS __stdcall mount_dokan_CloseFile(
                    const wchar_t *path,
                    DOKAN_FILE_INFO *file_info );
#endif

