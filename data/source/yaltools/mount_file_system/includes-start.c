#include <common.h>
#include <memory.h>
#include <narrow_string.h>
#include <system_string.h>
#include <types.h>
#include <wide_string.h>

#if defined( HAVE_SYS_STAT_H )
#include <sys/stat.h>
#endif

#if defined( HAVE_SYS_TIME_H )
#include <sys/time.h>
#endif

#include <time.h>

#include "${tools_name}_${library_name}.h"
#include "${tools_name}_libcerror.h"
#include "mount_file_system.h"
#include "mount_path_string.h"
