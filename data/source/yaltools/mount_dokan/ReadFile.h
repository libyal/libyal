#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_ReadFile(
               const wchar_t *path,
               void *buffer,
               DWORD number_of_bytes_to_read,
               DWORD *number_of_bytes_read,
               LONGLONG offset,
               DOKAN_FILE_INFO *file_info );
#else
NTSTATUS __stdcall mount_dokan_ReadFile(
                    const wchar_t *path,
                    void *buffer,
                    DWORD number_of_bytes_to_read,
                    DWORD *number_of_bytes_read,
                    LONGLONG offset,
                    DOKAN_FILE_INFO *file_info );
#endif

