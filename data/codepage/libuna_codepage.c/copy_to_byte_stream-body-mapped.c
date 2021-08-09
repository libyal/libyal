	else if( ( unicode_character >= ${first_unicode_value} )
	      && ( unicode_character < ${last_unicode_value} ) )
	{
		unicode_character -= ${first_unicode_value};

		byte_stream_value = libuna_codepage_${codepage_name}_unicode_to_byte_stream_base_${first_unicode_value}[ unicode_character ];
	}
