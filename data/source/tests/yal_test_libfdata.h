/*
 * The libfdata header wrapper
 *
 * Copyright (C) ${copyright}, ${tests_authors}
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

#if !defined( _${library_name_suffix:upper_case}_TEST_LIBFDATA_H )
#define _${library_name_suffix:upper_case}_TEST_LIBFDATA_H

#include <common.h>

/* Define HAVE_LOCAL_LIBFDATA for local use of libfdata
 */
#if defined( HAVE_LOCAL_LIBFDATA )

#include <libfdata_area.h>
#include <libfdata_definitions.h>
#include <libfdata_list.h>
#include <libfdata_list_element.h>
#include <libfdata_range_list.h>
#include <libfdata_stream.h>
#include <libfdata_types.h>
#include <libfdata_vector.h>

#else

/* If libtool DLL support is enabled set LIBFDATA_DLL_IMPORT
 * before including libfdata.h
 */
#if defined( _WIN32 ) && defined( DLL_IMPORT )
#define LIBFDATA_DLL_IMPORT
#endif

#include <libfdata.h>

#endif /* defined( HAVE_LOCAL_LIBFDATA ) */

#endif /* !defined( _${library_name_suffix:upper_case}_TEST_LIBFDATA_H ) */

