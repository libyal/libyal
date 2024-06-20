		byte_stream_copy_to_${structure_member.data_type}_${structure_member.byte_order}(
		 ( (${prefix}_${structure_name}_t *) data )->${structure_member.name},
		 value_${structure_member.value_size}bit );
		libcnotify_printf(
		 "%s: ${structure_member.description}${tab_alignment}: ${format_indicator}\n",
		 function,
		 value_${structure_member.value_size}bit );

