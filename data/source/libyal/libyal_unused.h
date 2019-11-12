/*
 * Definitions to silence compiler warnings about unused function attributes/parameters.
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

#if !defined( _${library_name_upper_case}_UNUSED_H )
#define _${library_name_upper_case}_UNUSED_H

#include <common.h>

#if !defined( ${library_name_upper_case}_ATTRIBUTE_UNUSED )
#if defined( __GNUC__ ) && __GNUC__ >= 3
#define ${library_name_upper_case}_ATTRIBUTE_UNUSED	__attribute__ ((__unused__))
#else
#define ${library_name_upper_case}_ATTRIBUTE_UNUSED
#endif
#endif

#if defined( _MSC_VER )
#define ${library_name_upper_case}_UNREFERENCED_PARAMETER( parameter ) \
	UNREFERENCED_PARAMETER( parameter );
#else
#define ${library_name_upper_case}_UNREFERENCED_PARAMETER( parameter ) \
	/* parameter */
#endif

#endif /* !defined( _${library_name_upper_case}_UNUSED_H ) */

