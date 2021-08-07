	if( unicode_character < 0x0080 )
	{
		byte_stream_value = (uint16_t) unicode_character;
	}
/* TODO */
	byte_stream[ *byte_stream_index ] = (uint8_t) ( byte_stream_value & 0x00ff );

	byte_stream_value >>= 8;

	if( byte_stream_value != 0 )
	{
		*byte_stream_index += 1;

		byte_stream[ *byte_stream_index ] = (uint8_t) ( byte_stream_value & 0x00ff );
	}
	*byte_stream_index += 1;

	return( 1 );
}

