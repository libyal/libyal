dnl Checks for libcsplit required headers and functions
dnl
dnl Version: 20181117

dnl Function to detect if libcstring is available
dnl ac_libcstring_dummy is used to prevent AC_CHECK_LIB adding unnecessary -l<library> arguments
AC_DEFUN([AX_LIBCSTRING_CHECK_LIB],
  [AS_IF(
    [test "x$ac_cv_enable_shared_libs" = xno || test "x$ac_cv_with_libcstring" = xno],
    [ac_cv_libcstring=no],
    [dnl Check if the directory provided as parameter exists
    AS_IF(
      [test "x$ac_cv_with_libcstring" != x && test "x$ac_cv_with_libcstring" != xauto-detect],
      [AS_IF(
        [test -d "$ac_cv_with_libcstring"],
        [CFLAGS="$CFLAGS -I${ac_cv_with_libcstring}/include"
        LDFLAGS="$LDFLAGS -L${ac_cv_with_libcstring}/lib"],
        [AC_MSG_FAILURE(
          [no such directory: $ac_cv_with_libcstring],
          [1])
        ])
        ac_cv_libcstring=check],
      [dnl Check for a pkg-config file
      AS_IF(
        [test "x$cross_compiling" != "xyes" && test "x$PKGCONFIG" != "x"],
        [PKG_CHECK_MODULES(
          [libcstring],
          [libcstring >= 20120701],
          [ac_cv_libcstring=yes],
          [ac_cv_libcstring=check])
        ])
      AS_IF(
        [test "x$ac_cv_libcsplit" = xyes && test "x$ac_cv_enable_wide_character_type" != xno],
        [AC_CACHE_CHECK(
         [whether libcsplit/features.h defines LIBCSPLIT_HAVE_WIDE_CHARACTER_TYPE as 1],
         [ac_cv_header_libcsplit_features_h_have_wide_character_type],
         [AC_LANG_PUSH(C)
         AC_COMPILE_IFELSE(
           [AC_LANG_PROGRAM(
             [[#include <libcsplit/features.h>]],
             [[#if !defined( LIBCSPLIT_HAVE_WIDE_CHARACTER_TYPE ) || ( LIBCSPLIT_HAVE_WIDE_CHARACTER_TYPE != 1 )
#error LIBCSPLIT_HAVE_WIDE_CHARACTER_TYPE not defined
#endif]] )],
           [ac_cv_header_libcsplit_features_h_have_wide_character_type=yes],
           [ac_cv_header_libcsplit_features_h_have_wide_character_type=no])
         AC_LANG_POP(C)],
         [ac_cv_header_libcsplit_features_h_have_wide_character_type=no])

        AS_IF(
          [test "x$ac_cv_header_libcsplit_features_h_have_wide_character_type" = xno],
          [ac_cv_libcsplit=no])
        ])
      AS_IF(
        [test "x$ac_cv_libcstring" = xyes],
        [ac_cv_libcstring_CPPFLAGS="$pkg_cv_libcstring_CFLAGS"
        ac_cv_libcstring_LIBADD="$pkg_cv_libcstring_LIBS"])
      ])

    AS_IF(
      [test "x$ac_cv_libcstring" = xcheck],
      [dnl Check for headers
      AC_CHECK_HEADERS([libcstring.h])

      AS_IF(
        [test "x$ac_cv_header_libcstring_h" = xno],
        [ac_cv_libcstring=no],
        [dnl Check for the individual functions
        ac_cv_libcstring=yes

        AC_CHECK_LIB(
          cstring,
          libcstring_get_version,
          [ac_cv_libcstring_dummy=yes],
          [ac_cv_libcstring=no])

        dnl Narrow string functions
        AC_CHECK_LIB(
          csplit,
          libcsplit_narrow_string_split,
          [ac_cv_libcsplit_dummy=yes],
          [ac_cv_libcsplit=no])

        dnl Narrow split string functions
        AC_CHECK_LIB(
          csplit,
          libcsplit_narrow_split_string_free,
          [ac_cv_libcsplit_dummy=yes],
          [ac_cv_libcsplit=no])
        AC_CHECK_LIB(
          csplit,
          libcsplit_narrow_split_string_get_string,
          [ac_cv_libcsplit_dummy=yes],
          [ac_cv_libcsplit=no])
        AC_CHECK_LIB(
          csplit,
          libcsplit_narrow_split_string_get_number_of_segments,
          [ac_cv_libcsplit_dummy=yes],
          [ac_cv_libcsplit=no])
        AC_CHECK_LIB(
          csplit,
          libcsplit_narrow_split_string_get_segment_by_index,
          [ac_cv_libcsplit_dummy=yes],
          [ac_cv_libcsplit=no])
        AC_CHECK_LIB(
          csplit,
          libcsplit_narrow_split_string_set_segment_by_index,
          [ac_cv_libcsplit_dummy=yes],
          [ac_cv_libcsplit=no])

        dnl Wide string functions
        AS_IF(
          [test "x$ac_cv_enable_wide_character_type" != xno],
          [AC_CHECK_LIB(
            csplit,
            libcsplit_wide_string_split,
            [ac_cv_libcsplit_dummy=yes],
            [ac_cv_libcsplit=no])

        dnl Wide split string functions
          AC_CHECK_LIB(
            csplit,
            libcsplit_wide_split_string_free,
            [ac_cv_libcsplit_dummy=yes],
            [ac_cv_libcsplit=no])
          AC_CHECK_LIB(
            csplit,
            libcsplit_wide_split_string_get_string,
            [ac_cv_libcsplit_dummy=yes],
            [ac_cv_libcsplit=no])
          AC_CHECK_LIB(
            csplit,
            libcsplit_wide_split_string_get_number_of_segments,
            [ac_cv_libcsplit_dummy=yes],
            [ac_cv_libcsplit=no])
          AC_CHECK_LIB(
            csplit,
            libcsplit_wide_split_string_get_segment_by_index,
            [ac_cv_libcsplit_dummy=yes],
            [ac_cv_libcsplit=no])
          AC_CHECK_LIB(
            csplit,
            libcsplit_wide_split_string_set_segment_by_index,
            [ac_cv_libcsplit_dummy=yes],
            [ac_cv_libcsplit=no])
          ])

        ac_cv_libcstring_LIBADD="-lcstring"])
      ])
    AS_IF(
      [test "x$ac_cv_with_libcstring" != x && test "x$ac_cv_with_libcstring" != xauto-detect && test "x$ac_cv_libcstring" != xyes],
      [AC_MSG_FAILURE(
        [unable to find supported libcstring in directory: $ac_cv_with_libcstring],
        [1])
      ])
    ])

  AS_IF(
    [test "x$ac_cv_libcstring" = xyes],
    [AC_DEFINE(
      [HAVE_LIBCSTRING],
      [1],
      [Define to 1 if you have the `cstring' library (-lcstring).])
    ])

  AS_IF(
    [test "x$ac_cv_libcstring" = xyes],
    [AC_SUBST(
      [HAVE_LIBCSTRING],
      [1]) ],
    [AC_SUBST(
      [HAVE_LIBCSTRING],
      [0])
    ])
  ])

dnl Function to detect if libcsplit dependencies are available
AC_DEFUN([AX_LIBCSPLIT_CHECK_LOCAL],
  [dnl No additional checks.

  ac_cv_libcsplit_CPPFLAGS="-I../libcsplit";
  ac_cv_libcsplit_LIBADD="../libcsplit/libcsplit.la";

  ac_cv_libcsplit=local
  ])

dnl Function to detect how to enable libcsplit
AC_DEFUN([AX_LIBCSPLIT_CHECK_ENABLE],
  [AX_COMMON_ARG_WITH(
    [libcsplit],
    [libcsplit],
    [search for libcsplit in includedir and libdir or in the specified DIR, or no if to use local version],
    [auto-detect],
    [DIR])

  dnl Check for a shared library version
  AX_LIBCSPLIT_CHECK_LIB

  dnl Check if the dependencies for the local library version
  AS_IF(
    [test "x$ac_cv_libcsplit" != xyes],
    [AX_LIBCSPLIT_CHECK_LOCAL

    AC_DEFINE(
      [HAVE_LOCAL_LIBCSPLIT],
      [1],
      [Define to 1 if the local version of libcsplit is used.])
    AC_SUBST(
      [HAVE_LOCAL_LIBCSPLIT],
      [1])
    ])

  AM_CONDITIONAL(
    [HAVE_LOCAL_LIBCSPLIT],
    [test "x$ac_cv_libcsplit" = xlocal])
  AS_IF(
    [test "x$ac_cv_libcsplit_CPPFLAGS" != "x"],
    [AC_SUBST(
      [LIBCSPLIT_CPPFLAGS],
      [$ac_cv_libcsplit_CPPFLAGS])
    ])
  AS_IF(
    [test "x$ac_cv_libcsplit_LIBADD" != "x"],
    [AC_SUBST(
      [LIBCSPLIT_LIBADD],
      [$ac_cv_libcsplit_LIBADD])
    ])

  AS_IF(
    [test "x$ac_cv_libcsplit" = xyes],
    [AC_SUBST(
      [ax_libcsplit_pc_libs_private],
      [-lcsplit])
    ])

  AS_IF(
    [test "x$ac_cv_libcsplit" = xyes],
    [AC_SUBST(
      [ax_libcsplit_spec_requires],
      [libcsplit])
    AC_SUBST(
      [ax_libcsplit_spec_build_requires],
      [libcsplit-devel])
    ])
  ])

