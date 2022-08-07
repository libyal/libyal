/*
 * Huffman tree functions
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

#if !defined( _${library_name_upper_case}_HUFFMAN_TREE_H )
#define _${library_name_upper_case}_HUFFMAN_TREE_H

#include <common.h>
#include <types.h>

#include "${library_name}_bit_stream.h"
#include "${library_name}_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

typedef struct ${library_name}_huffman_tree ${library_name}_huffman_tree_t;

struct ${library_name}_huffman_tree
{
	/* The maximum number of bits allowed for a Huffman code
	 */
	uint8_t maximum_code_size;

	/* The symbols array
	 */
	uint16_t *symbols;

	/* The code size counts array
	 */
	int *code_size_counts;
};

int ${library_name}_huffman_tree_initialize(
     ${library_name}_huffman_tree_t **huffman_tree,
     int number_of_symbols,
     uint8_t maximum_code_size,
     libcerror_error_t **error );

int ${library_name}_huffman_tree_free(
     ${library_name}_huffman_tree_t **huffman_tree,
     libcerror_error_t **error );

int ${library_name}_huffman_tree_build(
     ${library_name}_huffman_tree_t *huffman_tree,
     const uint8_t *code_sizes_array,
     int number_of_code_sizes,
     libcerror_error_t **error );

int ${library_name}_huffman_tree_get_symbol_from_bit_stream(
     ${library_name}_huffman_tree_t *huffman_tree,
     ${library_name}_bit_stream_t *bit_stream,
     uint16_t *symbol,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name_upper_case}_HUFFMAN_TREE_H ) */

