#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to format source of the libyal libraries."""

from __future__ import print_function
import sys

import source_formatter


if __name__ == '__main__':
  formatter = source_formatter.SourceFormatter()
  lines = formatter.FormatSource(sys.stdin.readlines())

  print(b''.join(lines), end=b'')
  
