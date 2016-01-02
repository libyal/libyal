/*
 * Codepage functions
 *
 * Copyright (C) ${copyright}, ${authors}
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

#if !defined( _${library_name_upper_case}_INTERNAL_CODEPAGE_H )
#define _${library_name_upper_case}_INTERNAL_CODEPAGE_H

#include <common.h>
#include <types.h>

#if defined( __cplusplus )
extern "C" {
#endif

#if !defined( HAVE_LOCAL_${library_name_upper_case} )

#include <${library_name}/codepage.h>

/* Define HAVE_LOCAL_${library_name_upper_case} for local use of ${library_name}
 * The definitions in <${library_name}/codepage.h> are copied here
 * for local use of ${library_name}
 */
#else

/* The codepage definitions
 */
enum ${library_name_upper_case}_CODEPAGES
{
	${library_name_upper_case}_CODEPAGE_ASCII				= 20127,

	${library_name_upper_case}_CODEPAGE_ISO_8859_1			= 28591,
	${library_name_upper_case}_CODEPAGE_ISO_8859_2			= 28592,
	${library_name_upper_case}_CODEPAGE_ISO_8859_3			= 28593,
	${library_name_upper_case}_CODEPAGE_ISO_8859_4			= 28594,
	${library_name_upper_case}_CODEPAGE_ISO_8859_5			= 28595,
	${library_name_upper_case}_CODEPAGE_ISO_8859_6			= 28596,
	${library_name_upper_case}_CODEPAGE_ISO_8859_7			= 28597,
	${library_name_upper_case}_CODEPAGE_ISO_8859_8			= 28598,
	${library_name_upper_case}_CODEPAGE_ISO_8859_9			= 28599,
	${library_name_upper_case}_CODEPAGE_ISO_8859_10			= 28600,
	${library_name_upper_case}_CODEPAGE_ISO_8859_11			= 28601,
	${library_name_upper_case}_CODEPAGE_ISO_8859_13			= 28603,
	${library_name_upper_case}_CODEPAGE_ISO_8859_14			= 28604,
	${library_name_upper_case}_CODEPAGE_ISO_8859_15			= 28605,
	${library_name_upper_case}_CODEPAGE_ISO_8859_16			= 28606,

	${library_name_upper_case}_CODEPAGE_KOI8_R				= 20866,
	${library_name_upper_case}_CODEPAGE_KOI8_U				= 21866,

	${library_name_upper_case}_CODEPAGE_WINDOWS_874			= 874,
	${library_name_upper_case}_CODEPAGE_WINDOWS_932			= 932,
	${library_name_upper_case}_CODEPAGE_WINDOWS_936			= 936,
	${library_name_upper_case}_CODEPAGE_WINDOWS_949			= 949,
	${library_name_upper_case}_CODEPAGE_WINDOWS_950			= 950,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1250			= 1250,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1251			= 1251,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1252			= 1252,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1253			= 1253,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1254			= 1254,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1255			= 1255,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1256			= 1256,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1257			= 1257,
	${library_name_upper_case}_CODEPAGE_WINDOWS_1258			= 1258
};

#endif /* !defined( HAVE_LOCAL_${library_name_upper_case} ) */

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_upper_case}_INTERNAL_CODEPAGE_H ) */

