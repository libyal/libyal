	${structure_member.name}      = &( data[ data_offset ] );
	${structure_member.name}_size = 0;

	while( ( data_offset + 1 ) < data_size )
	{
		${structure_member.name}_size += 2;

		if( ( data[ data_offset ] == 0 )
		 && ( data[ data_offset + 1 ] == 0 ) )
		{
			break;
		}
		data_offset += 2;
	}
	data_offset += 2;

