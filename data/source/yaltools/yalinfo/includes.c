#include <common.h>
#include <file_stream.h>
#include <memory.h>
#include <system_string.h>
#include <types.h>

#include <stdio.h>

#if defined( HAVE_IO_H ) || defined( WINAPI )
#include <io.h>
#endif

#if defined( HAVE_STDLIB_H ) || defined( WINAPI )
#include <stdlib.h>
#endif

#if defined( HAVE_UNISTD_H )
#include <unistd.h>
#endif

#include "info_handle.h"
#include "${tools_name}_getopt.h"
#include "${tools_name}_libcerror.h"
#include "${tools_name}_libclocale.h"
#include "${tools_name}_libcnotify.h"
#include "${tools_name}_${library_name}.h"
#include "${tools_name}_output.h"
#include "${tools_name}_signal.h"
#include "${tools_name}_unused.h"

