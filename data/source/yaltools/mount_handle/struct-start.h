typedef struct mount_handle mount_handle_t;

struct mount_handle
{
	/* The basename
	 */
	system_character_t *basename;

	/* The basename size
	 */
	size_t basename_size;

	/* The file system
	 */
	mount_file_system_t *file_system;

