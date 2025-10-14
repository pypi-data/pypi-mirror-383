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
TestCases for testing the locking sub-system.
"""

import time
import unittest
from test.support.os_helper import rmtree

from berkeleydb import db
from .test_all import get_new_environment_path

from threading import Thread

#----------------------------------------------------------------------

class LockingTestCase(unittest.TestCase):
    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()
        self.env.open(self.homeDir, db.DB_THREAD | db.DB_INIT_MPOOL |
                                    db.DB_INIT_LOCK | db.DB_CREATE)


    def tearDown(self):
        self.env.close()
        rmtree(self.homeDir)


    def test01_simple(self):
        anID = self.env.lock_id()
        lock = self.env.lock_get(anID, "some locked thing", db.DB_LOCK_WRITE)
        self.env.lock_put(lock)
        self.env.lock_id_free(anID)


    def test02_threaded(self):
        threads = []
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_WRITE,)))
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_READ,)))
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_READ,)))
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_WRITE,)))
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_READ,)))
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_READ,)))
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_WRITE,)))
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_WRITE,)))
        threads.append(Thread(target = self.theThread,
                              args=(db.DB_LOCK_WRITE,)))

        for t in threads:
            t.daemon = True
            t.start()
        for t in threads:
            t.join()

    def test03_lock_timeout(self):
        self.env.set_timeout(0, db.DB_SET_LOCK_TIMEOUT)
        self.assertEqual(self.env.get_timeout(db.DB_SET_LOCK_TIMEOUT), 0)
        self.env.set_timeout(0, db.DB_SET_TXN_TIMEOUT)
        self.assertEqual(self.env.get_timeout(db.DB_SET_TXN_TIMEOUT), 0)
        self.env.set_timeout(123456, db.DB_SET_LOCK_TIMEOUT)
        self.assertEqual(self.env.get_timeout(db.DB_SET_LOCK_TIMEOUT), 123456)
        self.env.set_timeout(7890123, db.DB_SET_TXN_TIMEOUT)
        self.assertEqual(self.env.get_timeout(db.DB_SET_TXN_TIMEOUT), 7890123)

    def test04_lock_timeout2(self):
        self.env.set_timeout(0, db.DB_SET_LOCK_TIMEOUT)
        self.env.set_timeout(0, db.DB_SET_TXN_TIMEOUT)
        self.env.set_timeout(123456, db.DB_SET_LOCK_TIMEOUT)
        self.env.set_timeout(7890123, db.DB_SET_TXN_TIMEOUT)

        def deadlock_detection() :
            while not deadlock_detection.end :
                deadlock_detection.count = \
                    self.env.lock_detect(db.DB_LOCK_EXPIRE)
                if deadlock_detection.count :
                    while not deadlock_detection.end :
                        pass
                    break
                time.sleep(0.01)

        deadlock_detection.end=False
        deadlock_detection.count=0
        t=Thread(target=deadlock_detection)
        t.daemon = True
        t.start()
        self.env.set_timeout(100000, db.DB_SET_LOCK_TIMEOUT)
        anID = self.env.lock_id()
        anID2 = self.env.lock_id()
        self.assertNotEqual(anID, anID2)
        lock = self.env.lock_get(anID, "shared lock", db.DB_LOCK_WRITE)
        start_time=time.time()
        self.assertRaises(db.DBLockNotGrantedError,
                self.env.lock_get,anID2, "shared lock", db.DB_LOCK_READ)
        end_time=time.time()
        deadlock_detection.end=True
        # Floating point rounding
        self.assertTrue((end_time-start_time) >= 0.0999)
        self.env.lock_put(lock)
        t.join()

        self.env.lock_id_free(anID)
        self.env.lock_id_free(anID2)

        self.assertTrue(deadlock_detection.count>0)

    def test05_not_None(self):
        anID = self.env.lock_id()
        try:
            self.assertRaises(TypeError, self.env.lock_get,
                              anID, None, db.DB_LOCK_WRITE)
        finally:
            self.env.lock_id_free(anID)

    def test06_stat(self):
        stats = self.env.lock_stat()
        if db.version() >= (6, 2):
            self.assertEqual(len(stats), 51)
        elif db.version() >= (5, 3):
            self.assertEqual(len(stats), 49)
        elif db.version() >= (4, 8):
            self.assertEqual(len(stats), 42)
        else:
            raise RuntimeError('Unknown Berkeley DB version')

        self.assertIn('cur_maxid', stats)
        self.assertIn('ndowngrade', stats)

    def theThread(self, lockType):
        anID = self.env.lock_id()

        for i in range(1000) :
            lock = self.env.lock_get(anID, "some locked thing", lockType)
            self.env.lock_put(lock)

        self.env.lock_id_free(anID)


#----------------------------------------------------------------------

def test_suite():
    suite = unittest.TestSuite()
    for test in (LockingTestCase,):
        test = unittest.defaultTestLoader.loadTestsFromTestCase(test)
        suite.addTest(test)

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
