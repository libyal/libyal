	${structure_member.name}      = &( data[ data_offset ] );
	${structure_member.name}_size = 0;

	while( data_offset < data_size )
	{
		${structure_member.name}_size += 1;

		if( data[ data_offset ] == 0 )
		{
			break;
		}
		data_offset += 1;
	}
	data_offset += 1;

