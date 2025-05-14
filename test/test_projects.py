import unittest
from goosvc.goosvc import Goosvc

USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_project"

class TestProjects(unittest.TestCase):
    def setUp(self):
        self.gvc = Goosvc("data-test")

    def test_create_project(self):
        projects_before = self.gvc.get_project_names(USER_NAME)
        r = self.gvc.create_project(USER_NAME, PROJECT_NAME)
        self.assertTrue(r)
        projects_after = self.gvc.get_project_names(USER_NAME)
        self.assertEqual(len(projects_after), len(projects_before) + 1)
        self.assertIn(PROJECT_NAME, projects_after)

    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)
