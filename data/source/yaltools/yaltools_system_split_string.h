/*
 * Split system string functions
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

#if !defined( _${tools_name:upper_case}_SYSTEM_SPLIT_STRING_H )
#define _${tools_name:upper_case}_SYSTEM_SPLIT_STRING_H

#include <common.h>
#include <types.h>

#include "${tools_name}_libcsplit.h"

#if defined( __cplusplus )
extern "C" {
#endif

#if defined( HAVE_WIDE_SYSTEM_CHARACTER )
#define system_split_string_t \
	libcsplit_wide_split_string_t

#define system_split_string_free( split_string, error ) \
	libcsplit_wide_split_string_free( split_string, error )

#define system_split_string_get_number_of_segments( split_string, number_of_segments, error ) \
	libcsplit_wide_split_string_get_number_of_segments( split_string, number_of_segments, error )

#define system_split_string_get_segment_by_index( split_string, segment_index, string_segment, string_segment_size, error ) \
	libcsplit_wide_split_string_get_segment_by_index( split_string, segment_index, string_segment, string_segment_size, error )

#define system_string_split( string, string_size, delimiter, split_string, error ) \
	libcsplit_wide_string_split( string, string_size, (wchar_t) delimiter, split_string, error )

#else
#define system_split_string_t \
	libcsplit_narrow_split_string_t

#define system_split_string_free( split_string, error ) \
	libcsplit_narrow_split_string_free( split_string, error )

#define system_split_string_get_number_of_segments( split_string, number_of_segments, error ) \
	libcsplit_narrow_split_string_get_number_of_segments( split_string, number_of_segments, error )

#define system_split_string_get_segment_by_index( split_string, segment_index, string_segment, string_segment_size, error ) \
	libcsplit_narrow_split_string_get_segment_by_index( split_string, segment_index, string_segment, string_segment_size, error )

#define system_string_split( string, string_size, delimiter, split_string, error ) \
	libcsplit_narrow_string_split( string, string_size, (char) delimiter, split_string, error )

#endif /* defined( HAVE_WIDE_SYSTEM_CHARACTER ) */

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${tools_name:upper_case}_SYSTEM_SPLIT_STRING_H ) */

