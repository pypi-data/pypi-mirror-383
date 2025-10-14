Changelog
=========

18.1.16 - XXXX-XX-XX
--------------------

18.1.15 - 2025-10-13
--------------------

  - .. warning::

       **WARNING - BREAKING CHANGE:** Drop support for Python 3.9.

       This breaking change should usually require a major and/or
       minor number update. Since ``berkeleydb`` traditional
       numbering is related to the higher Oracle Berkeley DB
       supported, I would usually wait until Oracle releases a new
       version to upgrade my own version and deprecate old Python
       support at the same time. Given that Oracle has not
       released a new Oracle Berkeley DB in almost five years, I
       must break this practice for now.

       I am sorry if this update breaks your Python 3.9
       environment. In that case, please pin your ``berkeleydb``
       installation to version 18.1.14, the last Python 3.9
       compatible release.

       Send me constructive feedback if appropriate.

  - Python 3.14 is officially supported.

  - Since we have drop Python 3.9:

    - We can simplify the code:

      - We can now freely use ``PyType_GetModuleState()``,
        ``PyModule_GetState()`` and ``PyType_GetModule()``.

      - We don't need ``Py_tp_new`` anymore in ``PyType_Slot`` types.

      - We can use ``PyType_FromModuleAndSpec()``.

      - Ease use of ``rmtree`` and ``unlink`` in tests.

    - We can use ``Py_TPFLAGS_DISALLOW_INSTANTIATION`` in all
      supported Python versions.

  - Now we require ``setuptools`` >= 80.9.0, so now the license
    must reencoded from ``License :: OSI Approved :: BSD License``
    to ``BSD-3-Clause``. They are the same license, no worries,
    but expressed in the syntax required by modern ``setuptools``.

  - Ugly workaround to be able to compile the bindings with GCC
    in pedantic mode.

  - Berkeley DB Exceptions are now compatible with Python
    subinterpreters. This is a big change, let me know if you find
    any problem, incompatibility or crash.

    This change increases the bindings C API version.

  - If we compile the bindings with mismatched header file and
    shared object, a descriptive exception is raised at import
    time.

  - In some funcions, booleans are now booleans, not integers.

  - Do **CLOSED** checks before argument parsing, to avoid memory
    leaks when there are problems.

18.1.14 - 2025-03-23
--------------------

  - .. warning::

       **WARNING - BREAKING CHANGE:** We eliminate ``dbobj.py``.
       It was very outdated and it was only barely useful if you
       wanted to create subclasses of **berkeleydb** classes.

       My recommended approach would be to use delegation instead
       of subclassing. It is quite trivial. Instead of subclassing
       ``DBEnv``, you can do something like::

        class My_DBEnv:
            def __init__(self, *args, **kwargs):
                self._cobj = db.DBEnv(*args, **kwargs)

            def __getattr__(self, name):
                return getattr(self._cobj, name)

       You can do something similar for other **berkeleydb**
       objects, for example, ``DB``, even implementing a *mapping*
       interface::

        class DB(MutableMapping):
            def __init__(self, dbenv, *args, **kwargs):
                # give it the proper DBEnv C object that its expecting
                self._cobj = db.DB(*((dbenv._cobj,) + args), **kwargs)

            def __getattr__(self, name):
                return getattr(self._cobj, name)

            # We need the following overrides because we are "MutableMapping".
            def __len__(self):
                return len(self._cobj)
            def __getitem__(self, arg):
                return self._cobj[arg]
            def __setitem__(self, key, value):
                self._cobj[key] = value
            def __delitem__(self, arg):
                del self._cobj[arg]
            def __iter__(self) :
                return self._cobj.__iter__()

  - Microsoft Windows support is back! Thanks to Brian Matthews
    <b.matthws@gmail.com> for pursuing this and for investing time
    and resources making it possible.

    I update the PyPI *Classifiers* for this project to from::

        Operating System :: Unix

    to::

        Operating System :: Unix
        Operating System :: POSIX
        Operating System :: Microsoft :: Windows

  - Allow unicode and binary keys when using encryption.
    Previously, only unicode keys were allowed. In both cases,
    null bytes (``'\0'`` or ``'\x00'``) will raise an exception.

  - Correctly display (in the raised exception) the type of the
    parameter when it is not accepted, beside the required type.
    This solves a regression introduced in 18.1.9.

  - Delete stale and outdated entries in the TO DO file.

  - Solve some redefinitions in the dictionary returned by
    ``DBEnv.lock_stat()`` and add more entries:

    - Berkeley DB >= 4.8: ``locksteals``, ``maxhlocks``,
      ``maxhobjects``, ``maxlsteals``, ``maxosteals``,
      ``objectsteals``, ``part_max_nowait``, ``part_max_wait``,
      ``part_nowait``, ``part_wait``, ``partitions``.

    - Berkeley DB >= 5.3: ``initlocks``, ``initlockers``,
      ``initobjects``, ``lockers``, ``locks``, ``objects``,
      ``tablesize``.

    - Berkeley DB >= 6.2: ``nlockers_hit``, ``nlockers_reused``.

  - Add more entries to ``DBEnv.log_stat()`` if we are using
    Berkeley DB >= 5.3: ``fileid_init``, ``maxnfileid``,
    ``nfileid``.

  - ``nelem`` value in ``DB.stat()`` for hash databases was
    dropped some time ago. Update stale documentation.

    That value is actually available via ``DB.get_h_nelem()``.

  - Improve docs explaining the ``end`` value in the dictionary
    returned by ``DB.compact()`` and documenting that
    ``empty_buckets`` is not available when using Berkeley DB 4.8.

  - In several *stats* dictionaries, document that ``ext_files``
    value is only available from Berkeley DB 6.2.

  - Add more entries to ``DBEnv.memp_stat()``: ``pagesize``.

  - Add more entries to ``DBEnv.memp_stat()`` if we are using
    Berkeley DB >= 5.3: ``regmax``, ``hash_mutexes``,
    ``backup_spins``.

  - Add more entries to ``DBEnv.memp_stat()`` if we are using
    Berkeley DB >= 6.2: ``mvcc_reused``.

  - Add more entries to ``DBEnv.txn_stat()`` if we are using
    Berkeley DB >= 5.3: ``inittxns``.

  - Add more entries to ``DBEnv.mutex_stat()`` if we are using
    Berkeley DB >= 5.3: ``mutex_init``, ``mutex_max``, ``regmax``.

  - Add more entries to ``DBEnv.repmgr_stat()`` if we are using
    Berkeley DB >= 5.3: ``elect_threads``, ``max_elect_threads``.

  - Add more entries to ``DBEnv.repmgr_stat()`` if we are using
    Berkeley DB >= 6.2: ``incoming_msgs_dropped``,
    ``incoming_queue_bytes``, ``incoming_queue_gbytes``,
    ``site_participants``, ``site_total``, ``site_views``,
    ``takeovers``, ``write_ops_forwarded``,
    ``write_ops_received``.

  - Add more entries to ``DBEnv.repmgr_stat()`` if we are using
    Berkeley DB >= 18.1: ``group_stable_log_file``,
    ``polling_method``.

  - Add more entries to ``DBEnv.rep_stat()`` if we are using
    Berkeley DB >= 5.3: ``election_datagen``, ``lease_chk``,
    ``lease_chk_misses``, ``lease_chk_refresh``, ``lease_sends``.

  - Add more entries to ``DBEnv.rep_stat()`` if we are using
    Berkeley DB >= 6.2: ``ext_duplicated``, ``ext_records``,
    ``ext_rereq``, ``ext_update_rereq``, ``view``.

  - In the different *stats* documentation, add notes about what
    versions of Berkeley DB provide the different values.

  - Complete documentation about *berkeleydb* exceptions and what
    Berkeley DB releases provide each one.

  - Document what functions are available when compiled against
    each Berkeley DB release.

18.1.13 - 2025-01-22
--------------------

  - .. note::

       Being able to compile the bindings on non x86/x86_64 Linux
       systems (ARM, RISC-V, etc).

       This improvement required to change the way compilation on
       Linux worked. If you find any issue with this, please
       report.

  - Compile the C module with extra static analysis and be more
    strict.

  - Some functions have unused parameters that we would like to
    preserve.

  - Different types in different python subinterpreters are tricky
    under Py_LIMITED_API < Python 3.10. We will delete the
    workarounds when Python 3.10 be the minimal supported version.

  - Delete some unused parameters thru all the source code.

  - Be explicit and complete in the sentinel values.

  - Be explicit initializing (missing) docstrings.

  - Rewrite some function prototypes to avoid warning when being
    strict and to avoid unneeded function castings.

    - Functions METH_NOARGS require two parameters, although one
      of them will be ignored.

  - Be sure we don't wrap an unsigned int operation, bypassing an
    assertion.

  - Update copyright to 2025.

18.1.12 - 2024-12-15
--------------------

  - .. warning::

       **WARNING - BREAKING CHANGE:** ``berkeleydb._db`` is now
       ``berkeleydb.db``.

       This breaking change should usually require a major and/or
       minor number update. Since ``berkeleydb`` traditional
       numbering is related to the higher Oracle Berkeley DB
       supported, I would usually wait until Oracle releases a new
       version to upgrade my own version and deprecate old Python
       support at the same time. Given that Oracle has not
       released a new Oracle Berkeley DB in almost five years, I
       must break this practice for now.

       The new name has been available for ages and the change is
       trivial...

  - Solved ``DBEnv.memp_stat()`` crash when no database was opened
    yet. Triaged and reported by Rishin Goswami.

  - Added a new ``DBError`` subclass exception:
    ``DBNotSupportedError``.

  - Add tests for environment and database encryption.

  - Document what you should know about your key when using
    database encryption. Check the docs!

  - Python 3.14 added to the full test matrix.

  - Experimental Python 3.14 support. Tested under 3.14.0a2.

  - Export more error codes from Oracle Berkeley DB (which ones
    depends of what Oracle Berkeley DB version you use):
    DB_FOREIGN_CONFLICT, DB_LOG_BUFFER_FULL, DB_LOG_VERIFY_BAD,
    DB_REP_HANDLE_DEAD, DB_REP_LOCKOUT, DB_REP_UNAVAIL,
    DB_REP_WOULDROLLBACK, DB_SLICE_CORRUPT, DB_VERSION_MISMATCH,
    DB_REP_INELECT, DB_SYSTEM_MEM_MISSING. Some of those are not
    actually returned ever, but a generic Berkeley DB exception is
    raised. The error codes are available for completion.

    If you need some specific exception to be raised, let me know.

  - We export more values from Oracle Berkeley DB (which ones
    depends of what Oracle Berkeley DB version you use):

    - DB_LOCK_GET_TIMEOUT, DB_LOCK_PUT_READ, DB_LOCK_TIMEOUT,
      DB_LOCK_TRADE.

    - DB_EID_MASTER.

    - DB_REP_WRITE_FORWARD_TIMEOUT.

    - DB_EVENT_REP_AUTOTAKEOVER, DB_EVENT_REP_INQUEUE_FULL,
      DB_EVENT_REP_JOIN_FAILURE, DB_EVENT_REP_WOULD_ROLLBACK,
      DB_EVENT_MUTEX_DIED, DB_EVENT_FAILCHK_PANIC.

    - DB_REPMGR_ISELECTABLE, DB_REPMGR_ISPEER,
      DB_REPMGR_CONF_DISABLE_POLL, DB_REPMGR_CONF_ENABLE_EPOLL,
      DB_REPMGR_CONF_FORWARD_WRITES,
      DB_REPMGR_CONF_PREFMAS_CLIENT,
      DB_REPMGR_CONF_PREFMAS_MASTER, DB_REPMGR_NEED_RESPONSE.

    - DB_MEM_DATABASE, DB_MEM_DATABASE_LENGTH,
      DB_MEM_EXTFILE_DATABASE, DB_MEM_REP_SITE.

    - DB_LOG_EXT_FILE.

    - DB_SET_MUTEX_FAILCHK_TIMEOUT.

    - DB_SLICED.

    - DB_VERB_BACKUP, DB_VERB_REPMGR_SSL_ALL,
      DB_VERB_REPMGR_SSL_CONN, DB_VERB_REPMGR_SSL_IO,
      DB_VERB_SLICE.

    - DB_XA_CREATE.

  - Oracle Berkeley DB>=5.3: Beside ``db.DB_VERSION_STRING`` we
    now have ``db.DB_VERSION_FULL_STRING``.

  - Oracle Berkeley DB>=6.2: Beside ``db.DB_DBT_BLOB`` we now have
    ``db.DB_DBT_EXT_FILE``.

  - Being able to test against an especific Oracle Berkeley DB
    release.

  - Code cleanup:

    - Remove unnecessary semicolons in Python code.
    - Remove unused imports.
    - Split multiple imports in a single line.
    - Split multiple statements in multiple lines.
    - Delete dead assignments.
    - Delete ancient code for ``verbose`` and ``silent`` in test
      code. I never used it, and it is maintenance load.
    - Simplify some ``assertTrue()`` and ``assertFalse()``.
    - Imports directly from ``berkeleydb`` instead of ``test_all``.
    - Copyright and license texts should be in comments, not
      docstrings.
    - Be more verbose and clear in the comparison test code.
    - Use ``isinstance()`` for type comparison.
    - Tight some tests.
    - Change some ambiguous variables.
    - Solve or silence ``ruff`` warnings.
    - Delete legacy ``pychecker`` support.
    - Delete legacy ``PyUnit GUI`` support.

18.1.11 - 2024-10-29
--------------------

  - .. warning::

       **WARNING - BREAKING CHANGE:** Drop support for Python 3.8.

       This breaking change should usually require a major and/or
       minor number update. Since ``berkeleydb`` traditional
       numbering is related to the higher Oracle Berkeley DB
       supported, I would usually wait until Oracle releases a new
       version to upgrade my own version and deprecate old Python
       support at the same time. Given that Oracle has not
       released a new Oracle Berkeley DB in almost five years, I
       must break this practice for now.

       I am sorry if this update breaks your Python 3.8
       environment. In that case, please pin your ``berkeleydb``
       installation to version 18.1.10, the last Python 3.8
       compatible release.

       Send me constructive feedback if appropriate.

  - Now that minimum Python supported is 3.9, all ``bsddb.db``
    objects support weakref in all supported Python versions.

  - Release 18.1.10 was failing under Python 2 because a charset
    encoding error. Since this module can not be used under
    Python 2 at all, we were not in a hurry to solve it and
    provide a more useful error message.

  - Solve some file leaks in some tests in the wrong directory.

  - Python 3.13 is officially supported.

18.1.10 - 2024-06-24
--------------------

  - Since MS Windows is unsupported without community help, I
    deleted some legacy code. It could be restored if there is
    demand and some help to improve MS Windows support.

  - New URL for :Oracle:`Oracle documentation <index.html>`.

  - Now we also use Python Stable ABI under Python 3.8 and 3.9.

    Under Python 3.10 and up we can define types that users can
    not instantiate as ``Py_TPFLAGS_DISALLOW_INSTANTIATION``, but
    that flag is not available under previous Python versions.

    In Python 3.8 and 3.9 we used to do ``type->tp_new = NULL;``
    for that, but this approach is not available under Python
    Stable ABI. That is the reason this module could use Python
    Stable ABI only when compiled under Python 3.10 and superior.

    In this release we define the slot ``Py_tp_new`` as ``NULL``
    in Python 3.8 and 3.9 to achieve the same effect, and that is
    available under Python Stable ABI.

  - Since this module can now use Python Stable ABI under all
    supported Python releases, that is exactly what we do. From
    now on this module always uses Python Stable ABI.

  - .. warning::

       **WARNING - BREAKING CHANGE:** Change return value of
       ``berkeleydb.py_limited_api()``.

       This function was introduced in 18.1.9 and it is used to
       indicate if the module was using the Python Stable ABI or
       not, and the version Python Stable ABI used.

       Now that the module has been improved to use Python Stable
       ABI always, the function returns a tuple of integers. First
       tuple element tells us what Python Stable ABI version are
       we supporting. Second element tells us what Python release
       was this module compiled under, although it should work in
       any more recent Python release.

       Since this function was introduced in release 18.1.9, we
       consider this breaking change a minor infraction affecting
       most probably nobody.

  - Delete some unneeded ancient Python 2.x code.

  - Delete more unneeded code to check threading support since
    Python 3.7 and up always guarantee threads.

18.1.9 - 2024-06-19
-------------------

  - ``pkg_resources`` is deprecated, so migrate to
    ``packaging``. This is already provided by modern
    ``setuptools``. This change only affects you if you run the
    test suite.

  - If compiled under Python 3.10 or higher, we use the Python
    Stable ABI, as defined in PEP 384 and related PEPs. That is,
    you can use the same compiled module with any Python release
    if Python version >= 3.10.

    In order to achieve this, we have made these changes:

    - Some fast Python API (not error checking) have been replaced
      by somewhat slower functions (functions that do error
      checking), because the former are not available in the
      Stable ABI: ``PyBytes_GET_SIZE()``, ``PyBytes_AS_STRING()``,
      ``PyTuple_SET_ITEM()``.

    - We replaced ``PyErr_Warn()`` by ``PyErr_WarnEx()`` because
      it is not available in the Stable ABI.

    - When an exception is raised because an incompatible type,
      we need to write complicated code because
      ``Py_TYPE(keyobj)->tp_name`` is not available in the Stable
      ABI. Code generated for Python < 3.11 is "ugly", we will
      clean it up when the minimum supported Python version is
      3.11.

    - ``TYPE->tp_alloc`` is not available under the Stable ABI. We
      replace it with ``PyType_GenericNew()``.

    - Internal types that should NOT be instanciated by the user
      has ``type->tp_new = NULL``. This can not be done under the
      Stable ABI, so we use ``Py_TPFLAGS_DISALLOW_INSTANTIATION``
      flag. This is the reason we only create Stable ABI modules
      under Python >= 3.10, because that flag is defined in that
      Python release.

    - The new function ``berkeleydb.py_limited_api()`` returns an
      integer describing the minimum supported Stable ABI or
      ``None``. If ``None``, the module is not compiled with
      Stable ABI and can not be used with a different Python
      version. When not ``None``, the value of
      ``berkeleydb.py_limited_api()`` can be easily interpreted
      using something like ``hex(berkeleydb.py_limited_api())``.

  - Python 3.13 added to the full test matrix.

  - Experimental Python 3.13 support. Tested under 3.13.0b2.

  - This code can be compiled under MS Windows, but I am unable to
    provide support for it and it is far from trivial. Because of
    this and some complains about it, I change the *Classifiers*
    for this project from

      **Operating System :: OS Independent**

    to

      **Operating System :: Unix**

    I would restore MS Windows support if there is some kind of
    community support for it. I can not do it by myself alone.
    Sorry about that.

18.1.8 - 2023-10-05
-------------------

  - .. warning::

       **WARNING - BREAKING CHANGE:** Drop support for Python 3.7.

       This breaking change should usually require a major and/or
       minor number update. Since ``berkeleydb`` traditional
       numbering is related to the higher Oracle Berkeley DB
       supported, I would usually wait until Oracle releases a new
       version to upgrade my own version and deprecate old Python
       support at the same time. Given that Oracle has not
       released a new Oracle Berkeley DB in almost five years, I
       must break this practice for now.

       I am sorry if this update breaks your Python 3.7
       environment. In that case, please pin your ``berkeleydb``
       installation to version 18.1.6, the last Python 3.7
       compatible release.

       Send me constructive feedback if appropriate.

  - Progressing the implementation of PEP 489 – Multi-phase
    extension module initialization:
    https://peps.python.org/pep-0489/.

    - Types are now private per sub-interpreter, if you are
      compiling under Python >= 3.9.

    - Provide a per sub-interpreter capsule object.

    - Solve a tiny race condition when importing the module in
      multiple sub-interpreters at the same time.

  - Update the "api_version" value of the capsule object.

  - Solve a "deprecation warning" when using modern
    ``setuptools``.

  - For testing, we require at least ``setuptools`` >= 62.1.0
    installed on all supported Python versions.

  - Python 3.12 is officially supported.

18.1.7 - 2023-10-05
-------------------

  - Yanked version.

18.1.6 - 2023-05-10
-------------------

  - Initial implementation of PEP 489 – Multi-phase extension
    module initialization: https://peps.python.org/pep-0489/.

  - Update ``setuptools`` built-time dependency to version
    ">=65.5.0". A "pip" modern enough will automatically take care
    of this.

  - We must be sure we are testing the correct library. Previously
    we could be testing the installed library instead of
    development code.

  - Python 3.12 added to the full test matrix.

  - Experimental Python 3.12 support. Tested under 3.12.0a7.

18.1.5 - 2022-01-21
-------------------

  - .. warning::

       **WARNING - BREAKING CHANGE:** Drop support for Python 3.6.

       This breaking change should usually require a major and/or
       minor number update. Since ``berkeleydb`` traditional
       numbering is related to the higher Oracle Berkeley DB
       supported, I would usually wait until Oracle releases a new
       version to upgrade my own version and deprecate old Python
       support at the same time. Given that Oracle has not
       released a new Oracle Berkeley DB in almost four years, I
       must break this practice for now.

       I am sorry if this update breaks your Python 3.6
       environment. In that case, please pin your ``berkeleydb``
       installation to version 18.1.4, the last Python 3.6
       compatible release.

       Send me constructive feedback if appropriate.

  - Python 3.10 support.

  - Testsuite works now in Python 3.11.0a4.

  - Python 3.11 added to the full test matrix.

  - Python 3.11 deprecates the ancient but undocumented method
    ``unittest.makeSuite()`` and it will be deleted in Python
    3.13. We migrate the tests to
    ``unittest.TestLoader.loadTestsFromTestCase()``.

  - Experimental Python 3.11 support. Tested in 3.11.0a4.

18.1.4 - 2021-05-19
-------------------

  - If your "pip" is modern enough, ``setuptools`` is
    automatically added as a built-time dependency.

    If not, you **MUST** install ``setuptools`` package first.

18.1.3 - 2021-05-19
-------------------

  - Docs in https://docs.jcea.es/berkeleydb/.

  - ``make publish`` build and publish the documentation online.

  - Python 3.10 deprecated ``distutils``. ``setuptools`` is now an
    installation dependency.

  - ``make dist`` will generate the HTML documentation and will
    include it in the released package. You can unpack the package
    to read the docs.

  - Do not install tests anymore when doing ``pip install``,
    although the tests are included in the package. You can unpack
    the package to study the tests, maybe in order to learn about
    how to use advanced Oracle Berkeley DB features.

    This change had an unexpected ripple effect in all code. Hopefully for the
    better.

  - Python 3.10 couldn't find build directory.

  - Python 3.10.0a2 test suite compatibility.

  - Python 3.10 added to the full test matrix.

  - After Python 3.7, threads are always available. Take them for granted,
    even in Python 3.6.

  - In the same direction, now some libraries are always available: pathlib,
    warnings, queue, gc.

  - Support ``DB.get_lk_exclusive()`` and
    ``DB.set_lk_exclusive()`` if you are linking against Oracle
    Berkeley DB 5.3 or newer.

  - .. warning::

       **WARNING - BREAKING CHANGE:** The record number in the
       tuple returned by ``DB.consume()`` is now a number instead
       of a binary key.

  - .. warning::

       **WARNING - BREAKING CHANGE:** The record number in the
       tuple returned by ``DB.consume_wait()`` is now a number
       instead of a binary key.

  - ``DB.consume()`` and ``DB.consume_wait()`` now can request
    partial records.

  - ``DB.get()`` and ``DB.pget()`` could misunderstand flags.

  - If you are using Oracle Berkeley DB 5.3 or newer, you have
    these new flags: ``DB_BACKUP_CLEAN``, ``DB_BACKUP_FILES``,
    ``DB_BACKUP_NO_LOGS``, ``DB_BACKUP_SINGLE_DIR`` and
    ``DB_BACKUP_UPDATE``, ``DB_BACKUP_WRITE_DIRECT``,
    ``DB_BACKUP_READ_COUNT``, ``DB_BACKUP_READ_SLEEP``,
    ``DB_BACKUP_SIZE``.

  - If you are using Oracle Berkeley DB 18.1 or newer, you have these new
    flags: ``DB_BACKUP_DEEP_COPY``.

  - ``DBEnv.backup()``, ``DBEnv.dbbackup()``
    ``DB.get_backup_config()`` and ``DB.set_backup_config()``
    available if you are using Oracle Berkeley DB 5.3 or newer.
    These methods allow you to do hot backups without needing to
    follow a careful procedure, and they can be incremental.

  - Changelog moved to Sphinx documentation.

18.1.2 - 2020-12-07
-------------------

  * Releases 18.1.0 and 18.1.1 were incomplete. Thanks to Mihai.i
    for reporting.

  * Export exception ``DBMetaChksumFail`` (from error
    ``DB_META_CHKSUM_FAIL``) if running Oracle Berkeley DB version
    6.2 or newer.

  * Support Heap access method if you are linking against Oracle Berkeley DB
    5.3 or newer.

    - ``DB.put()`` can add new records or overwrite old ones in
      Heap access method.

    - ``DB.append()`` was extended to support Heap access method.

    - ``DB.cursor()`` was extended to support Heap access method.

    - Implement, test and document ``DB.get_heapsize()``,
      ``DB.set_heapsize()``, ``DB.get_heap_regionsize()`` and
      ``DB.set_heap_regionsize()``.

    - Export exception ``DBHeapFull`` (from error
      ``DB_HEAP_FULL``).

    - ``DB.stats()`` provides stats for Heap access method.

  * .. warning::

      **WARNING - BREAKING CHANGE:** Add ``dbtype`` member in
      ``DBObject`` object in the C API. Increase C API version.
      This change has ripple effect in the code.

  * .. warning::

       **WARNING - BREAKING CHANGE:** ``primaryDBType`` member in
       ``DBObject`` object in the C API is now type ``DBTYPE``.
       Increase C API version. This change has ripple effect in
       the code.

  * Now ``DB.get_type()`` can be called anytime and it doesn't
    raise an exception if called before the database is open. If
    the database type is not known, ``DB_UNKNOWN`` is returned.
    This is a deviation from the Oracle Berkeley DB C API.

  * .. warning::

       **WARNING - BREAKING CHANGE:** ``DB.type()`` method is
       dropped. It was never documented. Use ``DB.get_type()``.

  * ``DB.stats()`` returns new keys in the dictionary:

    - Hash, Btree and Recno access methods: Added ``metaflags``
      (always) and ``ext_files`` (if linked against Oracle
      Berkeley DB 6.2 or newer).

    - Queue access method: Added ``metaflags`` (always).

18.1.1 - 2020-12-01
-------------------

  * If you try to install this library in an unsupported Python
    environment, instruct the user about how to install legacy
    ``bsddb3`` library.

  * Expose ``DBSite`` object in the C API. Increase C API version.

  * .. warning::

       **WARNING - BREAKING CHANGE:** Ancient release 4.2.8 added
       weakref support to all bsddb.db objects, but from now on
       this feature requires at least Python 3.9 because I have
       migrated from static types to heap types. Let me know if
       this is a problem for you. I could, for example, keep the
       old types in Python < 3.9, if needed.

       Details:

       Py_tp_dictoffset / Py_tp_finalize are unsettable in stable API
       https://bugs.python.org/issue38140

       bpo-38140: Make dict and weakref offsets opaque for C heap types (#16076)
       https://github.com/python/cpython/commit/3368f3c6ae4140a0883e19350e672fd09c9db616

  * ``_iter_mixin`` and ``_DBWithCursor`` classes have been
    rewritten to avoid the need of getting a weak reference to
    ``DBCursor`` objects, since now it is problematic if Python <
    3.9.

  * Wai Keen Woon and Nik Adam sent some weeks ago a patch to
    solve a problem with ``DB.verify()`` always succeeding.
    Refactoring in that area in 18.1.0 made that patch unneeded,
    but I added the test case provided to the test suite.

  * ``DBEnv.cdsgroup_begin()`` implemented.

  * ``DBTxn.set_priority()`` and ``DBTxn.get_priority()``
    implemented. You need to link this library against Oracle
    Berkeley DB >= 5.3.

  * ``DBEnv.set_lk_max()`` was deprecated and deleted long time
    ago. Time to delete it from documentation too.

  * .. warning::

       **WARNING - BREAKING CHANGE:** ``DB.compact()`` used to
       return a number, but now it returns a dictionary. If you
       need access to the old return value, you can do
       ``DB.compact()['pages_truncated']``.

  * ``DB.compact()`` has been supported ``txn`` parameter for a
    long time, but it was not documented.

  * The dictionary returned by ``DB.compact()`` has an ``end``
    entry marking the database key/page number where the
    compaction stopped. You could use it to do partial/incremental
    database compaction.

  * Add an optional parameter to ``DBEnv.log_flush()``.

  * You can override the directory where the tests are run with TMPDIR
    environment variable. If that environment variable is not
    defined, test will run in ``/tmp/ram/`` if exists and in
    ``/tmp`` if ``/tmp/ram/`` doesn't exists or it is not a
    directory. The idea is that ``/tmp/ram/`` is a ramdisk and the
    test will run faster.

18.1.0 - 2020-11-12
-------------------

  * ``bsddb`` name is reserved in PYPI, so we rename the project
    to ``berkeleydb``. This has been a long trip:
    http://mailman.jcea.es/pipermail/pybsddb/2008-March/000019.html

18.1.0-pre
----------

  * Support Oracle Berkeley DB 18.1.x.
  * Drop support for Oracle Berkeley DB 4.7, 5.1 and 6.1.
  * Drop support for Python 2.6, 2.7, 3.3, 3.4 and 3.5.
  * The library name is migrated from ``bsddb3`` to ``bsddb``. Reasons:

    - In the old days, ``bsddb`` module was integrated with Python < 3 . The
      release rate of new Python interpreters was slow, so ``bsddb`` was
      also distributed as an external package for faster deployment of
      improvements and support of new Oracle Berkeley DB releases. In order to
      be able to install a new version of this package without conflicting
      with the internal python ``bsddb``, a new package name was required.
      At the time, the chosen name was ``bsddb3`` because it was the major
      release version of the supported Oracle Berkeley DB library.

      After Oracle released Berkeley DB major versions 4, 5, 6 and 18, ``bsddb3``
      name was retained for compatibility, although it didn't make sense
      anymore.

    - ``bsddb3`` seems to refer to the Python 3 version of ``bsddb``. This
      was never the case, and that was confusing. Even more now that
      legacy ``bsddb3`` is the Python 2/3 codebase and the new ``bsddb`` is
      Python 3 only.

    - Since from now on this library is Python 3 only, I would hate that
      Python 2 users upgrading their Berkeley DB libraries would render
      their installation unable to run. In order to avoid that, a new name
      for the package is a good idea.

    - I decided to go back to ``bsddb``, since Python 2.7 is/should be dead.

    - If you are running Python 3, please update your code to use
      ``bsddb`` instead of ``bsddb3``.

      The old practice was to do:

          ``import bsddb3 as bsddb``

      Now you can change that to:

          ``import bsddb``

  * This library was usually know as ``bsddb``, ``bsddb3`` or ``pybsddb``.
    From now on, it is ``bsddb`` everywhere.
  * Testsuite driver migrated to Python 3.
  * Since Oracle Berkeley DB 4.7 is not supported anymore,
    ancient method ``DBEnv.set_rpc_server()`` is not available anymore.
  * If you try to install this package on Python 2,
    an appropriate error is raised and directions are provided.
  * Remove dead code for unsupported Python releases.
  * Remove dead code for unsupported Oracle Berkeley DB releases.
  * .. warning::

       **WARNING:** Now **ALL** keys and values must be bytes (or
       ints when appropriate). Previous releases did mostly
       transparent encoding. This is not the case anymore. All
       needed encoding must be explicit in your code, both when
       reading and when writing to the database.

  * In previous releases, database cursors were iterable under Python 3,
    but not under Python 2. For this release, database cursors are not
    iterable anymore. This will be improved in a future release.
  * In previous releases, log cursors were iterable under Python 3,
    but not under Python 2. For this release, log cursors are not
    iterable anymore. This will be improved in a future release.
  * Support for ``DB_REPMGR_CONF_DISABLE_SSL`` flag in
    ``DB_ENV.rep_set_config()``.
  * .. warning::

       **WARNING:** In Oracle Berkeley DB 18.1 and up, Replication
       Manager uses SSL by default.

       This configuration is currently unsupported.

       If you use Oracle Berkeley DB 18.1 and up and Replication
       Manager, you *MUST* configure the DB environment to not use
       SSL. You must do

          ``DB_ENV.rep_set_config(db.DB_REPMGR_CONF_DISABLE_SSL, 1)``

       in your code.

       This limitation will be overcomed in a future release of this project.

  * ``open()`` methods allow path-like objects.
  * ``DBEnv.open()`` accepts keyword arguments.
  * ``DBEnv.open()`` allows no homedir and a homedir of ``None``.
  * ``DB.set_re_source()`` uses local filename encoding.
  * ``DB.set_re_source()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB.verify()`` was doing nothing at all. Now actually do the job.
  * ``DB.verify()`` accepts path-like objects for ``filename`` and ``outfile`` if
    using Python 3.6 or up.
  * ``DB.upgrade()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB.remove()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB.remove()`` could leak objects.
  * ``DB.rename()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB.rename()`` correctly invalidates the DB handle.
  * ``DB.get_re_source()`` returns unicode objects with the local
    filename encoding.
  * ``DB_ENV.fileid_reset()`` accepts path-like objects if using Python 3.6 or
    up.
  * ``DB_ENV.log_file()`` correctly encode the filename according to the
    system FS encoding.
  * ``DB_ENV.log_archive()`` correctly encode the filenames according to the
    system FS encoding.
  * ``DB_ENV.lsn_reset()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB_ENV.remove()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB_ENV.remove()`` used to leave the DBENV handle in an unstable state.
  * ``DB_ENV.dbrename()`` accepts path-like objects for ``filename`` and ``newname``
    if using Python 3.6 or up.
  * ``DB_ENV.dbremove()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB_ENV.set_lg_dir()`` uses local filename encoding.
  * ``DB_ENV.set_lg_dir()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB_ENV.get_lg_dir()`` returns unicode objects with the local
    filename encoding.
  * ``DB_ENV.set_tmp_dir()`` uses local filename encoding.
  * ``DB_ENV.set_tmp_dir()`` accepts path-like objects if using Python 3.6 or up.
  * ``DB_ENV.get_tmp_dir()`` returns unicode objects with the local
    filename encoding.
  * ``DB_ENV.set_data_dir()`` uses local filename encoding.
  * ``DB_ENV.set_data_dir()`` accepts path-like objects if using Python 3.6 or
    up.
  * ``DB_ENV.get_data_dirs()`` returns a tuple of unicode objects encoded with
    the local filename encoding.
  * ``DB_ENV.log_prinf()`` requires a bytes object not containing '\0'.
  * The ``DB_ENV.lock_get()`` name can not be None.
  * ``DB_ENV.set_re_pad()`` param must be bytes or integer.
  * ``DB_ENV.get_re_pad()`` returns bytes.
  * ``DB_ENV.set_re_delim()`` param must be bytes or integer.
  * ``DB_ENV.get_re_delim()`` returns bytes.
  * In the C code we don't need ``statichere`` neither ``staticforward``
    workarounds anymore.
  * ``db.DB*`` objects are created via the native classes, not via
    factories anymore.
  * Drop support for ``dbtables``. If you need it back, let me know.
  * In Python 3.9, ``find_unused_port`` has been moved to
    ``test.support.socket_helper``. Reported by Michał Górny.
  * If we use ``set_get_returns_none()`` in the environment,
    the value could not be correctly inherited by the child
    databases. Reported by Patrick Laimbock and modern GCC
    warnings.
  * Do not leak test files and directories.
