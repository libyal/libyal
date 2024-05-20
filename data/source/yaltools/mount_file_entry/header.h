/*
 * Mount file entry
 *
 * Copyright (C) ${copyright}, ${tools_authors}
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#if !defined( _MOUNT_FILE_ENTRY_H )
#define _MOUNT_FILE_ENTRY_H

#include <common.h>
#include <types.h>

#include "mount_file_system.h"
#include "${tools_name}_libcerror.h"
#include "${tools_name}_${library_name}.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct mount_file_entry mount_file_entry_t;

struct mount_file_entry
{
	/* The file system
	 */
	mount_file_system_t *file_system;

	/* The name
	 */
	system_character_t *name;

	/* The name size
	 */
	size_t name_size;

	/* The ${mount_tool_file_entry_type_description}
	 */
	${library_name}_${mount_tool_file_entry_type}_t *${mount_tool_file_entry_type_name};
};

