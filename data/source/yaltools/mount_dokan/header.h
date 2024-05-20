/*
 * Mount tool dokan functions
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

#if !defined( _MOUNT_DOKAN_H )
#define _MOUNT_DOKAN_H

#include <common.h>
#include <types.h>

#if defined( HAVE_LIBDOKAN )
#include <dokan.h>
#endif

#include "mount_file_entry.h"
#include "${tools_name}_libcerror.h"
#include "${tools_name}_${library_name}.h"

#if defined( __cplusplus )
extern "C" {
#endif

#if defined( HAVE_LIBDOKAN )

int mount_dokan_set_file_information(
     BY_HANDLE_FILE_INFORMATION *file_information,
     size64_t size,
     uint16_t file_mode,
     uint64_t creation_time,
     uint64_t access_time,
     uint64_t modification_time,
     libcerror_error_t **error );

int mount_dokan_set_find_data(
     WIN32_FIND_DATAW *find_data,
     size64_t size,
     uint16_t file_mode,
     uint64_t creation_time,
     uint64_t access_time,
     uint64_t modification_time,
     libcerror_error_t **error );

int mount_dokan_filldir(
     PFillFindData fill_find_data,
     DOKAN_FILE_INFO *file_info,
     wchar_t *name,
     size_t name_size,
     WIN32_FIND_DATAW *find_data,
     mount_file_entry_t *file_entry,
     libcerror_error_t **error );

