from unittest import TestCase

import io
import os
import pureelib.plumbing.format as plumbing_format
import pureelib.plumbing.subspecs as plumbing_subspecs
import pureelib.plumbing.unpack as plumbing_unpack
import pureelib.plumbing.show as plumbing_show

MEBIBYTE = 1048576 # bytes
SECTOR = 512 # bytes

class FormatTests(TestCase):

    def test_format_then_show_disk(self):
        # Arrange a fake "3MiB disk"
        fake_disk_size = 3*MEBIBYTE
        with io.BytesIO(bytearray([0]*fake_disk_size)) as fake_disk:

            # Arrange a fake password
            password = "bpassword"

            # Pack the header to disk
            plumbing_format.puree_format(fake_disk, # device
                    fake_disk_size, 
                    plumbing_subspecs.DiskAes256XtsPlain64.subspec_name(), # cipher
                    None, # password_file
                    password, # password
                    False, # warn on password changes
                    False, # derive key from password
                    True  # show verbose output
                    )

            # Unpack the header
            headers = plumbing_unpack.puree_unpack(fake_disk,password)
            puree_salt = headers[0]
            box_one = headers[1]
            box_two = headers[2]

            # Assert
            plumbing_show.puree_show(headers,True)
            self.assertTrue(len(puree_salt) == 24)
            self.assertTrue(box_one.subspec == plumbing_subspecs.DiskAes256XtsPlain64.subspec_id())
            self.assertTrue(box_two.logical_start_sector == MEBIBYTE/SECTOR)
            self.assertTrue(box_two.num_sectors == MEBIBYTE/SECTOR)
            self.assertTrue(len(box_two.key) == 64)
