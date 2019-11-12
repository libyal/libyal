/*
 * Codepage definitions for ${library_name}
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

#if !defined( _${library_name_upper_case}_CODEPAGE_H )
#define _${library_name_upper_case}_CODEPAGE_H

#include <${library_name}/types.h>

#if defined( __cplusplus )
extern "C" {
#endif

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

#define ${library_name_upper_case}_CODEPAGE_US_ASCII			${library_name_upper_case}_CODEPAGE_ASCII

#define ${library_name_upper_case}_CODEPAGE_ISO_WESTERN_EUROPEAN		${library_name_upper_case}_CODEPAGE_ISO_8859_1
#define ${library_name_upper_case}_CODEPAGE_ISO_CENTRAL_EUROPEAN		${library_name_upper_case}_CODEPAGE_ISO_8859_2
#define ${library_name_upper_case}_CODEPAGE_ISO_SOUTH_EUROPEAN		${library_name_upper_case}_CODEPAGE_ISO_8859_3
#define ${library_name_upper_case}_CODEPAGE_ISO_NORTH_EUROPEAN		${library_name_upper_case}_CODEPAGE_ISO_8859_4
#define ${library_name_upper_case}_CODEPAGE_ISO_CYRILLIC			${library_name_upper_case}_CODEPAGE_ISO_8859_5
#define ${library_name_upper_case}_CODEPAGE_ISO_ARABIC			${library_name_upper_case}_CODEPAGE_ISO_8859_6
#define ${library_name_upper_case}_CODEPAGE_ISO_GREEK			${library_name_upper_case}_CODEPAGE_ISO_8859_7
#define ${library_name_upper_case}_CODEPAGE_ISO_HEBREW			${library_name_upper_case}_CODEPAGE_ISO_8859_8
#define ${library_name_upper_case}_CODEPAGE_ISO_TURKISH			${library_name_upper_case}_CODEPAGE_ISO_8859_9
#define ${library_name_upper_case}_CODEPAGE_ISO_NORDIC			${library_name_upper_case}_CODEPAGE_ISO_8859_10
#define ${library_name_upper_case}_CODEPAGE_ISO_THAI			${library_name_upper_case}_CODEPAGE_ISO_8859_11
#define ${library_name_upper_case}_CODEPAGE_ISO_BALTIC			${library_name_upper_case}_CODEPAGE_ISO_8859_13
#define ${library_name_upper_case}_CODEPAGE_ISO_CELTIC			${library_name_upper_case}_CODEPAGE_ISO_8859_14

#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_1			${library_name_upper_case}_CODEPAGE_ISO_8859_1
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_2			${library_name_upper_case}_CODEPAGE_ISO_8859_2
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_3			${library_name_upper_case}_CODEPAGE_ISO_8859_3
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_4			${library_name_upper_case}_CODEPAGE_ISO_8859_4
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_5			${library_name_upper_case}_CODEPAGE_ISO_8859_9
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_6			${library_name_upper_case}_CODEPAGE_ISO_8859_10
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_7			${library_name_upper_case}_CODEPAGE_ISO_8859_13
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_8			${library_name_upper_case}_CODEPAGE_ISO_8859_14
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_9			${library_name_upper_case}_CODEPAGE_ISO_8859_15
#define ${library_name_upper_case}_CODEPAGE_ISO_LATIN_10			${library_name_upper_case}_CODEPAGE_ISO_8859_16

#define ${library_name_upper_case}_CODEPAGE_KOI8_RUSSIAN			${library_name_upper_case}_CODEPAGE_KOI8_R
#define ${library_name_upper_case}_CODEPAGE_KOI8_UKRAINIAN			${library_name_upper_case}_CODEPAGE_KOI8_U

#define ${library_name_upper_case}_CODEPAGE_WINDOWS_THAI			${library_name_upper_case}_CODEPAGE_WINDOWS_874
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_JAPANESE		${library_name_upper_case}_CODEPAGE_WINDOWS_932
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_CHINESE_SIMPLIFIED	${library_name_upper_case}_CODEPAGE_WINDOWS_936
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_KOREAN			${library_name_upper_case}_CODEPAGE_WINDOWS_949
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_CHINESE_TRADITIONAL	${library_name_upper_case}_CODEPAGE_WINDOWS_950
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_CENTRAL_EUROPEAN	${library_name_upper_case}_CODEPAGE_WINDOWS_1250
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_CYRILLIC		${library_name_upper_case}_CODEPAGE_WINDOWS_1251
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_WESTERN_EUROPEAN	${library_name_upper_case}_CODEPAGE_WINDOWS_1252
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_GREEK			${library_name_upper_case}_CODEPAGE_WINDOWS_1253
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_TURKISH		${library_name_upper_case}_CODEPAGE_WINDOWS_1254
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_HEBREW			${library_name_upper_case}_CODEPAGE_WINDOWS_1255
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_ARABIC			${library_name_upper_case}_CODEPAGE_WINDOWS_1256
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_BALTIC			${library_name_upper_case}_CODEPAGE_WINDOWS_1257
#define ${library_name_upper_case}_CODEPAGE_WINDOWS_VIETNAMESE		${library_name_upper_case}_CODEPAGE_WINDOWS_1258

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_upper_case}_CODEPAGE_H ) */

