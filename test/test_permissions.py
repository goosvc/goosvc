import unittest
from goosvc.goosvc import Goosvc
from goosvc.core.projects import GoosvcPermission
from goosvc.core.nodes import GoosvcNode
from goosvc.core.exceptions import GoosvcException


OWNER_NAME = "test_owner"
USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_permissions"
TEST_TYPE1 = "test-type-1"


class TestPermissions(unittest.TestCase):
    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(OWNER_NAME, PROJECT_NAME)
    
    def tearDown(self):
        self.gvc.delete_project(OWNER_NAME, PROJECT_NAME)

    def test_set_access_permission(self):
        # owner
        permissions = self.gvc.get_access_permission(OWNER_NAME, PROJECT_NAME, OWNER_NAME)
        self.assertEqual(permissions.read, True)
        self.assertEqual(permissions.write, True)
        self.assertEqual(permissions.admin, True)
        # unknown user
        permissions = self.gvc.get_access_permission(OWNER_NAME, PROJECT_NAME, USER_NAME)
        self.assertEqual(permissions.read, False)
        self.assertEqual(permissions.write, False)
        self.assertEqual(permissions.admin, False)
        # app user (has all permissions)
        permissions = self.gvc.get_access_permission(OWNER_NAME, PROJECT_NAME, "app")
        self.assertEqual(permissions.read, True)
        self.assertEqual(permissions.write, True)
        self.assertEqual(permissions.admin, True)
        # add user
        user_permission = GoosvcPermission(read=True, write=True, admin=False)
        self.gvc.set_access_permission(OWNER_NAME, PROJECT_NAME, USER_NAME, user_permission)
        permissions = self.gvc.get_access_permission(OWNER_NAME, PROJECT_NAME, USER_NAME)
        self.assertEqual(permissions.read, True)
        self.assertEqual(permissions.write, True)
        self.assertEqual(permissions.admin, False)
        # change permissions
        user_permission.write = False
        self.gvc.set_access_permission(OWNER_NAME, PROJECT_NAME, USER_NAME, user_permission)
        permissions = self.gvc.get_access_permission(OWNER_NAME, PROJECT_NAME, USER_NAME)
        self.assertEqual(permissions.read, True)
        self.assertEqual(permissions.write, False)
        self.assertEqual(permissions.admin, False)
        # change permissions of owner (should not be possible)
        user_permission.write = False
        self.assertRaises(GoosvcException, self.gvc.set_access_permission, OWNER_NAME, PROJECT_NAME, OWNER_NAME, user_permission)
        permissions = self.gvc.get_access_permission(OWNER_NAME, PROJECT_NAME, OWNER_NAME)
        self.assertEqual(permissions.read, True)

    def test_public_private(self):
        project = self.gvc.get_project(OWNER_NAME, PROJECT_NAME)
        self.assertTrue(project.private)
        permissions = self.gvc.get_access_permission(OWNER_NAME, PROJECT_NAME, USER_NAME)
        self.assertEqual(permissions.read, False)
        self.assertEqual(permissions.write, False)
        self.assertEqual(permissions.admin, False)
        self.gvc.set_private(OWNER_NAME, PROJECT_NAME, False)
        project = self.gvc.get_project(OWNER_NAME, PROJECT_NAME)
        self.assertFalse(project.private)
        permissions = self.gvc.get_access_permission(OWNER_NAME, PROJECT_NAME, USER_NAME)
        self.assertEqual(permissions.read, True)
        self.assertEqual(permissions.write, False)
        self.assertEqual(permissions.admin, False)

    def test_permissions(self):
        # add node as user app user
        node1 = GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id1, node1_id = self.gvc.add_node(OWNER_NAME, PROJECT_NAME, node1)
        self.assertIsNotNone(branch_id1)
        # add node as owner
        node2 = GoosvcNode(TEST_TYPE1, branch_id1, OWNER_NAME, "test content 2")
        branch_id2, node2_id = self.gvc.add_node(OWNER_NAME, PROJECT_NAME, node2, OWNER_NAME)
        self.assertIsNotNone(branch_id2)
        # add node as unknown user
        node3 = GoosvcNode(TEST_TYPE1, branch_id1, "unknown", "test content 3")
        self.assertRaises(GoosvcException, self.gvc.add_node, OWNER_NAME, PROJECT_NAME, node3, "unknown")
        # read path as app user
        path = self.gvc.get_path(OWNER_NAME, PROJECT_NAME, branch_id2)
        self.assertEqual(len(path), 2)
        # read path as owner
        path = self.gvc.get_path(OWNER_NAME, PROJECT_NAME, branch_id2, [], None, OWNER_NAME)
        self.assertEqual(len(path), 2)
        # read path as unknown user
        self.assertRaises(GoosvcException, self.gvc.get_path, OWNER_NAME, PROJECT_NAME, branch_id2, [], None, "unknown")


