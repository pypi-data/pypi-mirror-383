# Copyright (c) 2008-2025, Jesús Cea Avión <jcea@jcea.es>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#     1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following
#     disclaimer in the documentation and/or other materials provided
#     with the distribution.
#
#     3. Neither the name of Jesús Cea Avión nor the names of its
#     contributors may be used to endorse or promote products derived
#     from this software without specific prior written permission.
#
#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
#     CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
#     INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
#     MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#     DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
#     BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#     EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#     TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#     DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#     ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
#     TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
#     THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#     SUCH DAMAGE.

"""TestCases for database encryption.
"""

import unittest
from test.support.os_helper import rmtree, unlink

from berkeleydb import db
from .test_all import get_new_environment_path, get_new_database_path

#----------------------------------------------------------------------

def test_support():
    database = db.DB()
    try:
        database.get_encrypt_flags()
    except db.DBNotSupportedError:
        return False
    else:
        return True
    finally:
        database.close()

encryption_supported = test_support()

#----------------------------------------------------------------------

@unittest.skipUnless(encryption_supported,
                     'Berkeley DB was compiled without encryption support')
class DBEnvEncryption(unittest.TestCase):
    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.dbenv = db.DBEnv()

    def tearDown(self):
        self.dbenv.close()
        rmtree(self.homeDir)

    def _open(self, dbenv):
        dbenv.open(self.homeDir,
                   db.DB_INIT_CDB | db.DB_INIT_MPOOL | db.DB_CREATE, 0o666)

    def test01_flags_no_encryption(self):
        flags = self.dbenv.get_encrypt_flags()
        self.assertEqual(flags, 0)

    def test02_no_key(self):
        self.assertRaises(db.DBInvalidArgError, self.dbenv.set_encrypt, '')

    def test03_key_string(self):
        self.dbenv.set_encrypt(self.key1)
        flags = self.dbenv.get_encrypt_flags()
        self.assertEqual(flags, 0)

    def test04_key_string_flags(self):
        self.dbenv.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
        flags = self.dbenv.get_encrypt_flags()
        self.assertEqual(flags, db.DB_ENCRYPT_AES)

    def test05_reopen_different_keys(self):
        self.dbenv.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
        self._open(self.dbenv)
        dbenv2 = db.DBEnv()
        try:
            dbenv2.set_encrypt(self.key2, flags=db.DB_ENCRYPT_AES)
            self.assertRaises(db.DBPermissionsError, self._open, dbenv2)
        finally:
            dbenv2.close()

    def test06_reopen_same_key(self):
        self.dbenv.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
        self._open(self.dbenv)
        dbenv2 = db.DBEnv()
        try:
            dbenv2.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
            self._open(dbenv2)
        finally:
            dbenv2.close()

    def test07_reopen_no_key(self):
        self.dbenv.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
        self._open(self.dbenv)
        dbenv2 = db.DBEnv()
        try:
            self.assertRaises(db.DBInvalidArgError, self._open, dbenv2)
        finally:
            dbenv2.close()

    def test08_reopen_no_encryption(self):
        self._open(self.dbenv)
        dbenv2 = db.DBEnv()
        try:
            dbenv2.set_encrypt(self.key2, flags=db.DB_ENCRYPT_AES)
            self.assertRaises(db.DBInvalidArgError, self._open, dbenv2)
        finally:
            dbenv2.close()

    def test09_file_implicit_encryption(self):
        self._open(self.dbenv)
        database = db.DB(self.dbenv)
        try:
            database.open('test', dbtype=db.DB_HASH, flags=db.DB_CREATE,
                          mode=0o666)
        finally:
            database.close()

    def test10_file_explicit_encryption(self):
        self._open(self.dbenv)
        database = db.DB(self.dbenv)
        try:
            self.assertRaises(db.DBInvalidArgError, database.set_encrypt,
                              self.key2, flags=db.DB_ENCRYPT_AES)
        finally:
            database.close()

    def test11_key_with_nulls(self):
        # Password can not contains NULL characters.
        key = '\x00'
        if isinstance(self.key1, bytes):
            key = b'\x00'
        self.assertRaises(ValueError, self.dbenv.set_encrypt, key)
        self.assertRaises(ValueError, self.dbenv.set_encrypt, key,
                          flags=db.DB_ENCRYPT_AES)

    def test12_key_invalid_types(self):
        for v in (17, None, bytearray(b'a')):
            self.assertRaisesRegex(TypeError,
                                   'Expected string or bytes argument, '
                                   fr'{type(v).__name__} found\.',
                                   self.dbenv.set_encrypt, v)
            self.assertRaisesRegex(TypeError,
                                   'Expected string or bytes argument, '
                                   fr'{type(v).__name__} found\.',
                                   self.dbenv.set_encrypt, v,
                                   flags=db.DB_ENCRYPT_AES)


class DBEnvEncryption_utf8(DBEnvEncryption):
    key1 = 'abc'
    key2 = 'XXX'


class DBEnvEncryption_binary(DBEnvEncryption):
    key1 = b'abc'
    key2 = b'XXX'


@unittest.skipUnless(encryption_supported,
                     'Berkeley DB was compiled without encryption support')
class DBEncryption(unittest.TestCase):
    def setUp(self):
        self.path = get_new_database_path()
        self.db = db.DB()

    def tearDown(self):
        self.db.close()
        unlink(self.path)

    def _open(self, database):
        database.open(self.path, dbtype=db.DB_HASH, flags=db.DB_CREATE,
                      mode=0o666)

    def test01_flags_no_encryption(self):
        flags = self.db.get_encrypt_flags()
        self.assertEqual(flags, 0)

    def test02_no_key(self):
        self.assertRaises(db.DBInvalidArgError, self.db.set_encrypt, '')

    def test03_key_string(self):
        self.db.set_encrypt(self.key1)
        flags = self.db.get_encrypt_flags()
        self.assertEqual(flags, 0)

    def test04_key_string_flags(self):
        self.db.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
        flags = self.db.get_encrypt_flags()
        self.assertEqual(flags, db.DB_ENCRYPT_AES)

    def test05_reopen_different_keys(self):
        self.db.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
        self._open(self.db)
        db2 = db.DB()
        try:
            db2.set_encrypt(self.key2, flags=db.DB_ENCRYPT_AES)
            if db.version() >= (5, 3):
                self.assertRaises(db.DBInvalidArgError, self._open, db2)
            else:
                # BerkeleyDB 4.8, generic error of "I don't know what
                # is that file, maybe corrupt" when encryption key doesn't
                # match.
                self.assertRaises(db.DBError, self._open, db2)
        finally:
            db2.close()

    def test06_reopen_same_key(self):
        self.db.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
        self._open(self.db)
        db2 = db.DB()
        try:
            db2.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
            self._open(db2)
        finally:
            db2.close()

    def test07_reopen_no_key(self):
        self.db.set_encrypt(self.key1, flags=db.DB_ENCRYPT_AES)
        self._open(self.db)
        db2 = db.DB()
        try:
            self.assertRaises(db.DBInvalidArgError, self._open, db2)
        finally:
            db2.close()

    def test08_reopen_no_encryption(self):
        self._open(self.db)
        db2 = db.DB()
        try:
            db2.set_encrypt(self.key2, flags=db.DB_ENCRYPT_AES)
            self.assertRaises(db.DBInvalidArgError, self._open, db2)
        finally:
            db2.close()

    def test09_key_with_nulls(self):
        # Password can not contains NULL characters.
        key = '\x00'
        if isinstance(self.key1, bytes):
            key = b'\x00'
        self.assertRaises(ValueError, self.db.set_encrypt, key)
        self.assertRaises(ValueError, self.db.set_encrypt, key,
                          flags=db.DB_ENCRYPT_AES)

    def test10_key_invalid_types(self):
        for v in (17, None, bytearray(b'a')):
            self.assertRaisesRegex(TypeError,
                                   'Expected string or bytes argument, '
                                   fr'{type(v).__name__} found\.',
                                   self.db.set_encrypt, v)
            self.assertRaisesRegex(TypeError,
                                   'Expected string or bytes argument, '
                                   fr'{type(v).__name__} found\.',
                                   self.db.set_encrypt, v,
                                   flags=db.DB_ENCRYPT_AES)


class DBEncryption_utf8(DBEncryption):
    key1 = 'abc'
    key2 = 'XXX'

class DBEncryption_binary(DBEncryption):
    key1 = b'abc'
    key2 = b'XXX'

#----------------------------------------------------------------------

def test_suite():
    suite = unittest.TestSuite()
    for test in (DBEnvEncryption_utf8, DBEnvEncryption_binary,
                 DBEncryption_utf8, DBEncryption_binary):
        test = unittest.defaultTestLoader.loadTestsFromTestCase(test)
        suite.addTest(test)

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
