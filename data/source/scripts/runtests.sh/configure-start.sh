CONFIGURE_HELP=`./configure --help`;

echo "$${CONFIGURE_HELP}" | grep -- '--enable-wide-character-type' > /dev/null;

HAVE_ENABLE_WIDE_CHARACTER_TYPE=$$?;

