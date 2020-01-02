
    ${library_name_suffix}_${type_name}.open(unittest.source)

    ${type_size_name} = ${library_name_suffix}_${type_name}.get_${type_size_name}()

    # Test normal read.
    data = ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, 0)

    self.assertIsNotNone(data)
    self.assertEqual(len(data), min(${type_size_name}, 4096))

    if ${type_size_name} > 8:
      # Read buffer on ${type_size_name} boundary.
      data = ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, ${type_size_name} - 8)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 8)

      # Read buffer beyond ${type_size_name} boundary.
      data = ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, ${type_size_name} + 8)

      self.assertIsNotNone(data)
      self.assertEqual(len(data), 0)

    # Stress test read buffer.
    for _ in range(1024):
      random_number = random.random()

      media_offset = int(random_number * ${type_size_name})
      read_size = int(random_number * 4096)

      data = ${library_name_suffix}_${type_name}.read_buffer_at_offset(read_size, media_offset)

      self.assertIsNotNone(data)

      remaining_${type_size_name} = ${type_size_name} - media_offset

      data_size = len(data)

      if read_size > remaining_${type_size_name}:
        read_size = remaining_${type_size_name}

      self.assertEqual(data_size, read_size)

      remaining_${type_size_name} -= data_size

      if not remaining_${type_size_name}:
        ${library_name_suffix}_${type_name}.seek_offset(0, os.SEEK_SET)

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.read_buffer_at_offset(-1, 0)

    with self.assertRaises(ValueError):
      ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, -1)

    ${library_name_suffix}_${type_name}.close()

    # Test the read without open.
    with self.assertRaises(IOError):
      ${library_name_suffix}_${type_name}.read_buffer_at_offset(4096, 0)
