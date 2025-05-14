import unittest
from goosvc.core import core


class TestCore(unittest.TestCase):
    def setUp(self):
        self.gvc = core.GoosvcCore("data-test")

    def test_basedir(self):
        base_dir = self.gvc.get_base_dir()
        self.assertEqual(base_dir, "data-test")