
	${member_name}      = &( data[ data_offset ] );
	${member_name}_size = 0;

	while( ( data_offset + 1 ) < data_size )
	{
		${member_name}_size += 2;

		if( ( data[ data_offset ] == 0 )
		 && ( data[ data_offset + 1 ] == 0 ) )
		{
			break;
		}
		data_offset += 2;
	}
	data_offset += 2;
