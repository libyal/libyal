#include <common.h>
#include <byte_stream.h>
#include <file_stream.h>
#include <types.h>

#if defined( HAVE_STDLIB_H ) || defined( WINAPI )
#include <stdlib.h>
#endif

#include "${prefix}_test_functions.h"
#include "${prefix}_test_libbfio.h"
#include "${prefix}_test_libcerror.h"
#include "${prefix}_test_${library_name}.h"
#include "${prefix}_test_macros.h"
#include "${prefix}_test_memory.h"
#include "${prefix}_test_unused.h"

#include "../${library_name}/${library_name}_${structure_name}.h"

