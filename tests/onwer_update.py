
import os.path
import unittest
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader, module_from_spec


def import_from_source(name, file_path):
    loader = SourceFileLoader(name, file_path)
    spec = spec_from_loader(loader.name, loader)
    module = module_from_spec(spec)
    loader.exec_module(module)
    return module


script_path = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..",
        "bin", "owner_update_1_7_18.py")
)
binscript = import_from_source("owner_update_1_7_18.py", script_path)


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
