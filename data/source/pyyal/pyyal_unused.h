/*
 * Definitions to silence compiler warnings about unused function attributes/parameters.
 *
 * Copyright (C) ${python_module_copyright}, ${python_module_authors}
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

#if !defined( _${python_module_name:upper_case}_UNUSED_H )
#define _${python_module_name:upper_case}_UNUSED_H

#include <common.h>

#if !defined( ${python_module_name:upper_case}_ATTRIBUTE_UNUSED )
#if defined( __GNUC__ ) && __GNUC__ >= 3
#define ${python_module_name:upper_case}_ATTRIBUTE_UNUSED	__attribute__ ((__unused__))
#else
#define ${python_module_name:upper_case}_ATTRIBUTE_UNUSED
#endif
#endif

#if defined( _MSC_VER )
#define ${python_module_name:upper_case}_UNREFERENCED_PARAMETER( parameter ) \
	UNREFERENCED_PARAMETER( parameter );
#else
#define ${python_module_name:upper_case}_UNREFERENCED_PARAMETER( parameter ) \
	/* parameter */
#endif

#endif /* !defined( _${python_module_name:upper_case}_UNUSED_H ) */

