import unittest
import sys
import os.path

sys.path.append(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
from bin import owner_update_1_7_18 as binscript  # noqa # pylint: disable=import-error


class TestConvertingOwnerURI(unittest.TestCase):

    def test_convert_old_scheme(self):
        # correct case
        self.assertEqual(r"personium-localunit:unitadmin:/#unitadmin",
                         binscript.convert_old_normalized_uri(r"personium-localunit:/unitadmin/#unitadmin"))

    def test_convert_old_scheme_with_malformed(self):
        # illegal case (malformed)
        self.assertEqual(r"personium-localunit:unitadmin:/#unitadmin",
                         binscript.convert_old_normalized_uri(r"personium-localunit:/unitadmin#unitadmin"))

    def test_convert_old_scheme_with_current_style(self):
        # illegal case (current-style)
        self.assertEqual(None,
                         binscript.convert_old_normalized_uri(r"personium-localunit:unitadmin:/#unitadmin"))

    def test_convert_old_scheme_with_not_localunit(self):
        # illegal case (not localunit-scheme)
        self.assertEqual(None,
                         binscript.convert_old_normalized_uri(r"https://dummy.pds.exmple.com/unitadmin#unitadmin"))


if __name__ == '__main__':
    unittest.main()
