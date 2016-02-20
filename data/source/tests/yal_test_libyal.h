/*
 * The internal liblnk header
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

#if !defined( _LNK_TEST_LIBLNK_H )
#define _LNK_TEST_LIBLNK_H

#include <common.h>

/* If Cygwin libtool DLL support is enabled set LIBLNK_DLL_IMPORT
 * before including liblnk.h
 */
#if defined( _WIN32 ) && defined( DLL_EXPORT )
#define LIBLNK_DLL_IMPORT
#endif

#include <liblnk.h>

#endif

