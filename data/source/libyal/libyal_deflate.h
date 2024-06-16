/*
 * Deflate (zlib) (un)compression functions
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

#if !defined( _${library_name:upper_case}_DEFLATE_COMPRESSION_H )
#define _${library_name:upper_case}_DEFLATE_COMPRESSION_H

#include <common.h>
#include <types.h>

#include "${library_name}_bit_stream.h"
#include "${library_name}_huffman_tree.h"
#include "${library_name}_libcerror.h"

#if defined( __cplusplus )
extern "C" {
#endif

/* The block types
 */
enum ${library_name:upper_case}_DEFLATE_BLOCK_TYPES
{
	${library_name:upper_case}_DEFLATE_BLOCK_TYPE_UNCOMPRESSED	= 0x00,
	${library_name:upper_case}_DEFLATE_BLOCK_TYPE_HUFFMAN_FIXED	= 0x01,
	${library_name:upper_case}_DEFLATE_BLOCK_TYPE_HUFFMAN_DYNAMIC	= 0x02,
	${library_name:upper_case}_DEFLATE_BLOCK_TYPE_RESERVED		= 0x03
};

int ${library_name}_deflate_build_dynamic_huffman_trees(
     ${library_name}_bit_stream_t *bit_stream,
     ${library_name}_huffman_tree_t *literals_tree,
     ${library_name}_huffman_tree_t *distances_tree,
     libcerror_error_t **error );

int ${library_name}_deflate_build_fixed_huffman_trees(
     ${library_name}_huffman_tree_t *literals_tree,
     ${library_name}_huffman_tree_t *distances_tree,
     libcerror_error_t **error );

int ${library_name}_deflate_decode_huffman(
     ${library_name}_bit_stream_t *bit_stream,
     ${library_name}_huffman_tree_t *literals_tree,
     ${library_name}_huffman_tree_t *distances_tree,
     uint8_t *uncompressed_data,
     size_t uncompressed_data_size,
     size_t *uncompressed_data_offset,
     libcerror_error_t **error );

int ${library_name}_deflate_calculate_adler32(
     uint32_t *checksum_value,
     const uint8_t *data,
     size_t data_size,
     uint32_t initial_value,
     libcerror_error_t **error );

int ${library_name}_deflate_read_data_header(
     const uint8_t *compressed_data,
     size_t compressed_data_size,
     size_t *compressed_data_offset,
     libcerror_error_t **error );

int ${library_name}_deflate_read_block_header(
     ${library_name}_bit_stream_t *bit_stream,
     uint8_t *block_type,
     uint8_t *last_block_flag,
     libcerror_error_t **error );

int ${library_name}_deflate_read_block(
     ${library_name}_bit_stream_t *bit_stream,
     uint8_t block_type,
     ${library_name}_huffman_tree_t *fixed_huffman_literals_tree,
     ${library_name}_huffman_tree_t *fixed_huffman_distances_tree,
     uint8_t *uncompressed_data,
     size_t uncompressed_data_size,
     size_t *uncompressed_data_offset,
     libcerror_error_t **error );

int ${library_name}_deflate_decompress(
     const uint8_t *compressed_data,
     size_t compressed_data_size,
     uint8_t *uncompressed_data,
     size_t *uncompressed_data_size,
     libcerror_error_t **error );

int ${library_name}_deflate_decompress_zlib(
     const uint8_t *compressed_data,
     size_t compressed_data_size,
     uint8_t *uncompressed_data,
     size_t *uncompressed_data_size,
     libcerror_error_t **error );

#if defined( __cplusplus )
}
#endif

#endif /* !defined( _${library_name:upper_case}_DEFLATE_COMPRESSION_H ) */

