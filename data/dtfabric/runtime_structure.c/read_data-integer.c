	byte_stream_copy_to_u${structure_member.data_type}_${structure_member.byte_order}(
	 ( (${prefix}_${structure_name}_t *) data )->${structure_member.name},
	 ${structure_name}->${structure_member.name} );

