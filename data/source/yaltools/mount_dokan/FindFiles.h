#if ( DOKAN_VERSION >= 600 ) && ( DOKAN_VERSION < 800 )
int __stdcall mount_dokan_FindFiles(
               const wchar_t *path,
               PFillFindData fill_find_data,
               DOKAN_FILE_INFO *file_info );
#else
NTSTATUS __stdcall mount_dokan_FindFiles(
                    const wchar_t *path,
                    PFillFindData fill_find_data,
                    DOKAN_FILE_INFO *file_info );
#endif

