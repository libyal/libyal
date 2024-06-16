/*
 * The libuna header wrapper
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

#if !defined( _${tools_name:upper_case}_LIBUNA_H )
#define _${tools_name:upper_case}_LIBUNA_H

#include <common.h>

/* Define HAVE_LOCAL_LIBUNA for local use of libuna
 */
#if defined( HAVE_LOCAL_LIBUNA )

#include <libuna_base16_stream.h>
#include <libuna_base32_stream.h>
#include <libuna_base64_stream.h>
#include <libuna_byte_stream.h>
#include <libuna_unicode_character.h>
#include <libuna_url_stream.h>
#include <libuna_utf16_stream.h>
#include <libuna_utf16_string.h>
#include <libuna_utf32_stream.h>
#include <libuna_utf32_string.h>
#include <libuna_utf7_stream.h>
#include <libuna_utf8_stream.h>
#include <libuna_utf8_string.h>
#include <libuna_types.h>

#else

/* If libtool DLL support is enabled set LIBUNA_DLL_IMPORT
 * before including libuna.h
 */
#if defined( _WIN32 ) && defined( DLL_IMPORT ) && !defined( HAVE_STATIC_EXECUTABLES )
#define LIBUNA_DLL_IMPORT
#endif

#include <libuna.h>

#endif /* defined( HAVE_LOCAL_LIBUNA ) */

#endif /* !defined( _${tools_name:upper_case}_LIBUNA_H ) */

