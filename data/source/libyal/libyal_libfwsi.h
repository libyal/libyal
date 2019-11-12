/*
 * The libfwsi header wrapper
 *
 * Copyright (C) ${copyright}, ${authors}
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

#if !defined( _${library_name_upper_case}_LIBFWSI_H )
#define _${library_name_upper_case}_LIBFWSI_H

#include <common.h>

/* Define HAVE_LOCAL_LIBFWSI for local use of libfwsi
 */
#if defined( HAVE_LOCAL_LIBFWSI )

#include <libfwsi_debug.h>
#include <libfwsi_definitions.h>
#include <libfwsi_extension_block.h>
#include <libfwsi_file_entry.h>
#include <libfwsi_file_entry_extension.h>
#include <libfwsi_item.h>
#include <libfwsi_item_list.h>
#include <libfwsi_known_folder_identifier.h>
#include <libfwsi_network_location.h>
#include <libfwsi_root_folder.h>
#include <libfwsi_shell_folder_identifier.h>
#include <libfwsi_types.h>
#include <libfwsi_volume.h>

#else

/* If libtool DLL support is enabled set LIBFWSI_DLL_IMPORT
 * before including libfwsi.h
 */
#if defined( _WIN32 ) && defined( DLL_IMPORT )
#define LIBFWSI_DLL_IMPORT
#endif

#include <libfwsi.h>

#endif /* defined( HAVE_LOCAL_LIBFWSI ) */

#endif /* !defined( _${library_name_upper_case}_LIBFWSI_H ) */

