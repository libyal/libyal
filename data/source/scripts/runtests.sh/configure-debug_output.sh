echo "$${CONFIGURE_HELP}" | grep -- '--enable-verbose-output' > /dev/null;

HAVE_ENABLE_VERBOSE_OUTPUT=$$?;

echo "$${CONFIGURE_HELP}" | grep -- '--enable-debug-output' > /dev/null;

HAVE_ENABLE_DEBUG_OUTPUT=$$?;

