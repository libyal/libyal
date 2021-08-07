	if( byte_stream_character < 0x80 )
	{
		safe_unicode_character = byte_stream_character;
	}
	else
	{
		byte_stream_character -= 0x80;

		safe_unicode_character = libuna_codepage_${codepage_name}_byte_stream_to_unicode_base_0x80[ byte_stream_character ];
	}
