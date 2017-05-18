#!/usr/bin/env python3
"Verify that checksum as extended attribute functionality is working correctly"

import hashlib
import logging
import os
import random
import shutil
import sys
import tempfile
import unittest

import xattr

LOG = logging.getLogger('s3fs_test')
LOG.level = logging.INFO
SH = logging.StreamHandler(sys.stdout)
LOG.addHandler(SH)

S3_MOUNT = '/tmp/s3_mount'

# Potential object size range, for randomly-generated objects
MIN_OBJ_SIZE = 50000        # 50kB
MAX_OBJ_SIZE = 10 * 1000**2 # 10MB

def random_file():
    "Generate a file with random contents, and return the file name"
    file_size = random.randint(MIN_OBJ_SIZE, MAX_OBJ_SIZE)
    fh = tempfile.NamedTemporaryFile(prefix='s3fs_checksum_test-', delete=False)
    fh.write(os.urandom(file_size))
    fh.close()
    return fh.name

def md5_file(name):
    "Return a hex string representing the md5 checksum of the file"
    h_obj = hashlib.md5()
    with open(name, "rb") as fh:
        h_obj.update(fh.read())
    return h_obj.hexdigest()

class TestChecksum(unittest.TestCase):
    "Test checksum extended attribute functionality"

    CHKSUM_ATTR = 'md5-checksum'

    def setUp(self):
        LOG.debug("Generating local file")
        self.local_file = random_file()
        LOG.debug("Generated file at: {0}".format(self.local_file))
        self.dest = os.path.join(S3_MOUNT, os.path.basename(self.local_file))

    def tearDown(self):
        LOG.debug("Removing local file {0}".format(self.local_file))
        os.unlink(self.local_file)
        if os.path.exists(self.dest):
            LOG.debug("Removing S3 object {0}".format(self.dest))
            os.unlink(self.dest)

    def test_1_add_checksum_meta(self):
        "Verify checksum is added to object"
        local_checksum = md5_file(self.local_file)
        shutil.copy(self.local_file, self.dest)
        try:
            s3_checksum = xattr.getxattr(self.dest, self.CHKSUM_ATTR).decode('utf-8')
        except OSError as err:
            if err.strerror == 'No data available':
                self.fail('missing {} extended attribute!'.format(self.CHKSUM_ATTR))
            else:
                raise
        self.assertEqual(local_checksum, s3_checksum, 'object checksum mismatch!')

if __name__ == "__main__":
    unittest.main(verbosity=2)
