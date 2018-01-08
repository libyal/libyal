

if __name__ == "__main__":
  argument_parser = argparse.ArgumentParser()

  ${argument_parser_options}

  options, unknown_options = argument_parser.parse_known_args()
  unknown_options.insert(0, sys.argv[0])

  ${unittest_options}

  unittest.main(argv=unknown_options, verbosity=2)
