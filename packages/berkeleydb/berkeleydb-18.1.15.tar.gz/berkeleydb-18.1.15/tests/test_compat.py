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

"""
Test cases adapted from the test_berkeleydb.py module in Python's
regression test suite.
"""

import os
import unittest

from berkeleydb import db, hashopen, btopen, rnopen
from .test_all import get_new_database_path


class CompatibilityTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = get_new_database_path()

    def tearDown(self):
        try:
            os.remove(self.filename)
        except os.error:
            pass


    def test01_btopen(self):
        self.do_bthash_test(btopen, 'btopen')

    def test02_hashopen(self):
        self.do_bthash_test(hashopen, 'hashopen')

    def test03_rnopen(self):
        data = b'The quick brown fox jumped over the lazy dog.'.split()

        f = rnopen(self.filename, 'c')
        for x in range(len(data)):
            f[x+1] = data[x]

        getTest = (f[1], f[2], f[3])

        self.assertEqual(getTest[1], b'quick', 'data mismatch!')

        rv = f.set_location(3)
        if rv != (3, b'brown'):
            self.fail('recno database set_location failed: '+repr(rv))

        f[25] = b'twenty-five'
        f.close()
        del f

        f = rnopen(self.filename, 'w')
        f[20] = b'twenty'

        def noRec(f):
            f[15]
        self.assertRaises(KeyError, noRec, f)

        def badKey(f):
            f[b'a string']
        self.assertRaises(TypeError, badKey, f)

        del f[3]

        rec = f.first()
        while rec:
            try:
                rec = f.next()
            except KeyError:
                break

        f.close()


    def test04_n_flag(self):
        f = hashopen(self.filename, 'n')
        f.close()


    def do_bthash_test(self, factory, what):
        f = factory(self.filename, 'c')
        # truth test
        if f:
            pass

        f[b'0'] = b''
        f[b'a'] = b'Guido'
        f[b'b'] = b'van'
        f[b'c'] = b'Rossum'
        f[b'd'] = b'invented'
        # b'e' intentionally left out
        f[b'f'] = b'Python'

        start = f.set_location(f.first()[0])
        if start != (b'0', b''):
            self.fail("incorrect first() result: "+repr(start))
        while True:
            try:
                rec = f.next()
            except KeyError:
                self.assertEqual(rec, f.last(), 'Error, last <> last!')
                f.previous()
                break

        self.assertTrue(b'f' in f, 'Error, missing key!')

        # test that set_location() returns the next nearest key, value
        # on btree databases and raises KeyError on others.
        if factory == btopen:
            e = f.set_location(b'e')
            if e != (b'f', b'Python'):
                self.fail('wrong key,value returned: '+repr(e))
        else:
            try:
                e = f.set_location(b'e')
            except KeyError:
                pass
            else:
                self.fail("set_location on non-existent key did not raise KeyError")

        f.sync()
        f.close()
        # truth test
        try:
            if f:
                pass
        except db.DBError:
            pass
        else:
            self.fail("Exception expected")

        del f

        f = factory(self.filename, 'w')
        f[b'd'] = b'discovered'

        for key in list(f.keys()):
            f[key]

        def noRec(f):
            f[b'no such key']
        self.assertRaises(KeyError, noRec, f)

        def badKey(f):
            f[15]
        self.assertRaises(TypeError, badKey, f)

        f.close()


#----------------------------------------------------------------------


def test_suite():
    suite = unittest.TestSuite()
    for test in (CompatibilityTestCase,):
        test = unittest.defaultTestLoader.loadTestsFromTestCase(test)
        suite.addTest(test)

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
