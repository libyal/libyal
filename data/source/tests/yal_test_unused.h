/*
 * The unused definition
 *
 * Copyright (C) ${copyright}, ${tests_authors}
 *
 * Refer to AUTHORS for acknowledgements.
 *
 * This software is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this software.  If not, see <http://www.gnu.org/licenses/>.
 */

#if !defined( _${library_name_suffix_upper_case}_TEST_UNUSED_H )
#define _${library_name_suffix_upper_case}_TEST_UNUSED_H

#include <common.h>

#if !defined( ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED )

#if defined( __GNUC__ ) && __GNUC__ >= 3
#define ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED	__attribute__ ((__unused__))

#else
#define ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED

#endif /* defined( __GNUC__ ) && __GNUC__ >= 3 */

#endif /* !defined( ${library_name_suffix_upper_case}_TEST_ATTRIBUTE_UNUSED ) */

#if defined( _MSC_VER )
#define ${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( parameter ) \
	UNREFERENCED_PARAMETER( parameter );

#else
#define ${library_name_suffix_upper_case}_TEST_UNREFERENCED_PARAMETER( parameter ) \
	/* parameter */

#endif /* defined( _MSC_VER ) */

#endif /* !defined( _${library_name_suffix_upper_case}_TEST_UNUSED_H ) */

