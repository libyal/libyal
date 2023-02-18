dnl Checks for libfwps required headers and functions
dnl
dnl Version: 20230130

dnl Function to detect if libfwps is available
dnl ac_libfwps_dummy is used to prevent AC_CHECK_LIB adding unnecessary -l<library> arguments
AC_DEFUN([AX_LIBFWPS_CHECK_LIB],
  [AS_IF(
    [test "x$ac_cv_enable_shared_libs" = xno || test "x$ac_cv_with_libfwps" = xno],
    [ac_cv_libfwps=no],
    [ac_cv_libfwps=check
    dnl Check if the directory provided as parameter exists
    AS_IF(
      [test "x$ac_cv_with_libfwps" != x && test "x$ac_cv_with_libfwps" != xauto-detect],
      [AS_IF(
        [test -d "$ac_cv_with_libfwps"],
        [CFLAGS="$CFLAGS -I${ac_cv_with_libfwps}/include"
        LDFLAGS="$LDFLAGS -L${ac_cv_with_libfwps}/lib"],
        [AC_MSG_FAILURE(
          [no such directory: $ac_cv_with_libfwps],
          [1])
        ])
      ],
      [dnl Check for a pkg-config file
      AS_IF(
        [test "x$cross_compiling" != "xyes" && test "x$PKGCONFIG" != "x"],
        [PKG_CHECK_MODULES(
          [libfwps],
          [libfwps >= 20230130],
          [ac_cv_libfwps=yes],
          [ac_cv_libfwps=check])
        ])
      AS_IF(
        [test "x$ac_cv_libfwps" = xyes],
        [ac_cv_libfwps_CPPFLAGS="$pkg_cv_libfwps_CFLAGS"
        ac_cv_libfwps_LIBADD="$pkg_cv_libfwps_LIBS"])
      ])

    AS_IF(
      [test "x$ac_cv_libfwps" = xcheck],
      [dnl Check for headers
      AC_CHECK_HEADERS([libfwps.h])

      AS_IF(
        [test "x$ac_cv_header_libfwps_h" = xno],
        [ac_cv_libfwps=no],
        [dnl Check for the individual functions
        ac_cv_libfwps=yes

        AC_CHECK_LIB(
          fwps,
          libfwps_get_version,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])

        dnl Store functions
        AC_CHECK_LIB(
          fwps,
          libfwps_store_initialize,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_store_free,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_store_copy_from_byte_stream,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])

        AC_CHECK_LIB(
          fwps,
          libfwps_store_get_number_of_sets,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_store_get_set_by_index,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])

        dnl Set functions
        AC_CHECK_LIB(
          fwps,
          libfwps_set_initialize,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_set_free,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_set_copy_from_byte_stream,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])

        dnl Record functions
        AC_CHECK_LIB(
          fwps,
          libfwps_record_free,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])

        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_entry_type,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_value_type,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])

        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_boolean,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_8bit_integer,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_16bit_integer,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_32bit_integer,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_64bit_integer,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_filetime,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_floating_point,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_utf8_string_size,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_utf8_string,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_utf16_string_size,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_utf16_string,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])
        AC_CHECK_LIB(
          fwps,
          libfwps_record_get_data_as_guid,
          [ac_cv_libfwps_dummy=yes],
          [ac_cv_libfwps=no])

        ac_cv_libfwps_LIBADD="-lfwps"])
      ])
    AS_IF(
      [test "x$ac_cv_with_libfwps" != x && test "x$ac_cv_with_libfwps" != xauto-detect && test "x$ac_cv_libfwps" != xyes],
      [AC_MSG_FAILURE(
        [unable to find supported libfwps in directory: $ac_cv_with_libfwps],
        [1])
      ])
    ])

  dnl Check for debug functions
  AS_IF(
    [test "x$ac_cv_libfwps" = xyes && test "x$ac_cv_enable_debug_output" != xno],
    [AC_CHECK_LIB(
      fwps,
      libfwps_property_identifier_get_description,
      [ac_cv_libfwps_dummy=yes],
      [ac_cv_libfwps=no])

    AC_CHECK_LIB(
      fwps,
      libfwps_property_identifier_get_identifier,
      [ac_cv_libfwps_dummy=yes],
      [ac_cv_libfwps=no])
    ])

  AS_IF(
    [test "x$ac_cv_libfwps" = xyes],
    [AC_DEFINE(
      [HAVE_LIBFWPS],
      [1],
      [Define to 1 if you have the `fwps' library (-lfwps).])
    ])

  AS_IF(
    [test "x$ac_cv_libfwps" = xyes],
    [AC_SUBST(
      [HAVE_LIBFWPS],
      [1]) ],
    [AC_SUBST(
      [HAVE_LIBFWPS],
      [0])
    ])
  ])

dnl Function to detect if libfwps dependencies are available
AC_DEFUN([AX_LIBFWPS_CHECK_LOCAL],
  [dnl No additional checks.

  ac_cv_libfwps_CPPFLAGS="-I../libfwps";
  ac_cv_libfwps_LIBADD="../libfwps/libfwps.la";

  ac_cv_libfwps=local
  ])

dnl Function to detect how to enable libfwps
AC_DEFUN([AX_LIBFWPS_CHECK_ENABLE],
  [AX_COMMON_ARG_WITH(
    [libfwps],
    [libfwps],
    [search for libfwps in includedir and libdir or in the specified DIR, or no if to use local version],
    [auto-detect],
    [DIR])

  dnl Check for a shared library version
  AX_LIBFWPS_CHECK_LIB

  dnl Check if the dependencies for the local library version
  AS_IF(
    [test "x$ac_cv_libfwps" != xyes],
    [AX_LIBFWPS_CHECK_LOCAL

    AC_DEFINE(
      [HAVE_LOCAL_LIBFWPS],
      [1],
      [Define to 1 if the local version of libfwps is used.])
    AC_SUBST(
      [HAVE_LOCAL_LIBFWPS],
      [1])
    ])

  AM_CONDITIONAL(
    [HAVE_LOCAL_LIBFWPS],
    [test "x$ac_cv_libfwps" = xlocal])
  AS_IF(
    [test "x$ac_cv_libfwps_CPPFLAGS" != "x"],
    [AC_SUBST(
      [LIBFWPS_CPPFLAGS],
      [$ac_cv_libfwps_CPPFLAGS])
    ])
  AS_IF(
    [test "x$ac_cv_libfwps_LIBADD" != "x"],
    [AC_SUBST(
      [LIBFWPS_LIBADD],
      [$ac_cv_libfwps_LIBADD])
    ])

  AS_IF(
    [test "x$ac_cv_libfwps" = xyes],
    [AC_SUBST(
      [ax_libfwps_pc_libs_private],
      [-lfwps])
    ])

  AS_IF(
    [test "x$ac_cv_libfwps" = xyes],
    [AC_SUBST(
      [ax_libfwps_spec_requires],
      [libfwps])
    AC_SUBST(
      [ax_libfwps_spec_build_requires],
      [libfwps-devel])
    ])
  ])

