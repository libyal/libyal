#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_GetFileInformation(
               const wchar_t *path,
               BY_HANDLE_FILE_INFORMATION *file_information,
               DOKAN_FILE_INFO *file_info );
#else
NTSTATUS __stdcall mount_dokan_GetFileInformation(
                    const wchar_t *path,
                    BY_HANDLE_FILE_INFORMATION *file_information,
                    DOKAN_FILE_INFO *file_info );
#endif

