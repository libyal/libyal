
    ${library_name_suffix}_${type_name}.open(unittest.source)

    ${type_size_name} = ${library_name_suffix}_${type_name}.get_${type_size_name}()

    if ${type_size_name} < 4096:
      # Test read without maximum size.
      ${library_name_suffix}_${type_name}.seek_offset(0, os.SEEK_SET)

      data = ${library_name_suffix}_${type_name}.read_buffer()

      self.assertIsNotNone(data)
      self.assertEqual(len(data), ${type_size_name})

    # Test read with maximum size.
    ${library_name_suffix}_${type_name}.seek_offset(0, os.SEEK_SET)

    data = ${library_name_suffix}_${type_name}.read_buffer(size=4096)

    self.assertIsNotNone(data)
    self.assertEqual(len(data), min(${type_size_name}, 4096))

    if ${type_size_name} > 8:
      ${library_name_suffix}_${type_name}.seek_offset(-8, os.SEEK_END)

      # Read buffer on ${type_size_name} boundary.
      data = ${library_name_suffix}_${type_name}.read_buffer(size=4096)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 8)

      # Read buffer beyond ${type_size_name} boundary.
      data = ${library_name_suffix}_${type_name}.read_buffer(size=4096)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 0)

    # Stress test read buffer.
    ${library_name_suffix}_${type_name}.seek_offset(0, os.SEEK_SET)

    remaining_${type_size_name} = ${type_size_name}

    for _ in range(1024):
      read_size = int(random.random() * 4096)

      data = ${library_name_suffix}_${type_name}.read_buffer(size=read_size)

      self.assertIsNotNone(data)

      data_size = len(data)

      if read_size > remaining_${type_size_name}:
        read_size = remaining_${type_size_name}

      self.assertEqual(data_size, read_size)

      remaining_${type_size_name} -= data_size

      if not remaining_${type_size_name}:
        ${library_name_suffix}_${type_name}.seek_offset(0, os.SEEK_SET)

        remaining_${type_size_name} = ${type_size_name}

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.read_buffer(size=-1)

    ${library_name_suffix}_${type_name}.close()

    # Test the read without open.
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.read_buffer(size=4096)
