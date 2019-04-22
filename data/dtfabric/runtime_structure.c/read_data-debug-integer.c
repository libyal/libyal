		byte_stream_copy_to_${data_type}_${byte_order}(
		 ( (${prefix}_${structure_name}_t *) data )->${member_name},
		 value_${bit_size}bit );
		libcnotify_printf(
		 "%s: ${member_name_description}${tab_alignment}: ${format_indicator}\n",
		 function,
		 value_${bit_size}bit );

