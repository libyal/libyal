/*
 * Definitions for ${codepage_description} codepage tests
 *
 * Copyright (C) ${copyright}, Joachim Metz <joachim.metz@gmail.com>
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

#if !defined( _UNA_TEST_CODEPAGE_${codepage_name:upper_case}_H )
#define _UNA_TEST_CODEPAGE_${codepage_name:upper_case}_H

#include <common.h>
#include <types.h>

#include "una_test_types.h"

#if defined( __cplusplus )
extern "C" {
#endif

una_test_byte_stream_to_unicode_t una_test_codepage_${codepage_name}_byte_stream_to_unicode[ ${number_of_test_mappings} ] = {
${test_mappings}
};

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _UNA_TEST_CODEPAGE_${codepage_name:upper_case}_H ) */

