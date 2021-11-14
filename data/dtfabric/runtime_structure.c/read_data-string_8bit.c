	${member_name}      = &( data[ data_offset ] );
	${member_name}_size = 0;

	while( data_offset < data_size )
	{
		${member_name}_size += 1;

		if( data[ data_offset ] == 0 )
		{
			break;
		}
		data_offset += 1;
	}
	data_offset += 1;

