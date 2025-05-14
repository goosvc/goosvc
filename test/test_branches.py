import unittest
from goosvc.goosvc import Goosvc
from goosvc.core.branches import BranchGroup

USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_nodes"
NODE1_ID = "0f94fa10df8e4c13a9cad440d04c7ac8"
NODE2_ID = "1f94fa10df8e4c13a9cad440d04c7ac8"
NODE3_ID = "2f94fa10df8e4c13a9cad440d04c7ac8"
UNKNOWN_BRANCH_ID = "cc55f0bd055641feac1f9d95f80e5a3f"
UNKNOWN_NODE_ID = "aa55f0bd055641feac1f9d95f80e5a3f"
UNKNOWN_GROUP_ID = "bb55f0bd055641feac1f9d95f80e5a3f"


class TestBranches(unittest.TestCase):

    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
        self.branches = self.gvc.core.branches
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)

    def test_add_branch(self):
        branches_before = self.branches.get_branches(USER_NAME,PROJECT_NAME)
        branch_id = self.branches.create_branch(USER_NAME,PROJECT_NAME,NODE1_ID)
        self.assertIsNotNone(branch_id)
        # check if the branch is in the branches
        branches_after = self.branches.get_branches(USER_NAME,PROJECT_NAME)
        self.assertIsNotNone(branches_after)
        self.assertEqual(len(branches_after), len(branches_before) + 1)
        self.assertIn(branch_id, branches_after)
        # check if the branch was created correctly
        branch_head = self.branches.get_branch_head(USER_NAME,PROJECT_NAME,branch_id)
        self.assertIsNotNone(branch_head)
        self.assertEqual(branch_head, NODE1_ID)
        # check if the branch is in the node
        branch_id_node = self.branches.get_branch_of_node(USER_NAME,PROJECT_NAME,NODE1_ID)
        self.assertIsNotNone(branch_id_node)
        self.assertEqual(branch_id_node, branch_id)
        # check get_branch_head with unknown branch
        branch_head = self.branches.get_branch_head(USER_NAME,PROJECT_NAME,UNKNOWN_BRANCH_ID)
        self.assertIsNone(branch_head)
        # check get_branch_of_node with unknown node
        branch_id_node = self.branches.get_branch_of_node(USER_NAME,PROJECT_NAME,UNKNOWN_NODE_ID)
        self.assertIsNone(branch_id_node)
        # update branch head
        self.branches.update_branch_head(USER_NAME,PROJECT_NAME,branch_id,NODE2_ID)
        branch_head = self.branches.get_branch_head(USER_NAME,PROJECT_NAME,branch_id)
        self.assertIsNotNone(branch_head)
        self.assertEqual(branch_head, NODE2_ID)
        # check if the branch is in the node
        branch_id_node = self.branches.get_branch_of_node(USER_NAME,PROJECT_NAME,NODE2_ID)
        self.assertIsNotNone(branch_id_node)
        self.assertEqual(branch_id_node, branch_id)
        # update branch head with unknown branch
        self.assertFalse(self.branches.update_branch_head(USER_NAME,PROJECT_NAME,UNKNOWN_BRANCH_ID,NODE2_ID))

    def test_branch_groups(self):
        # create branch group
        branch_id = self.branches.create_branch(USER_NAME,PROJECT_NAME,NODE1_ID)
        branch_id2 = self.branches.create_branch(USER_NAME,PROJECT_NAME,NODE2_ID)
        # check we have no groups yet
        groups = self.branches.get_branch_groups(USER_NAME,PROJECT_NAME)
        self.assertEqual(len(groups), 0)
        # create group with unknown branch
        branch_group_1 = BranchGroup([branch_id,UNKNOWN_BRANCH_ID],"test_group_1")
        group_id = self.branches.create_branch_group(USER_NAME,PROJECT_NAME,branch_group_1)
        self.assertIsNone(group_id)
        # create branch group
        branch_group_2 = BranchGroup([branch_id,branch_id2],"test_group_2")
        group_id = self.branches.create_branch_group(USER_NAME,PROJECT_NAME,branch_group_2)
        self.assertIsNotNone(group_id)
        # check if the group is in the branches
        groups = self.branches.get_branch_groups(USER_NAME,PROJECT_NAME)
        self.assertIsNotNone(groups)
        self.assertEqual(len(groups), 1)
        self.assertIn(group_id, groups)
        # check if the group was created correctly
        group_content = self.branches.get_branch_group(USER_NAME,PROJECT_NAME,group_id)
        self.assertIsNotNone(group_content)
        self.assertEqual(len(group_content.branch_ids), 2)
        self.assertIn(branch_id, group_content.branch_ids)
        self.assertIn(branch_id2, group_content.branch_ids)
        self.assertEqual(group_content.group_id, group_id)
        self.assertEqual(group_content.description, "test_group_2")
        # update with unknown group
        branch_group_3 = BranchGroup([branch_id,branch_id2],"test_group_3",UNKNOWN_GROUP_ID)
        self.assertFalse(self.branches.update_branch_group(USER_NAME,PROJECT_NAME,branch_group_3))
        # update with invalid branch id
        branch_group_4 = BranchGroup([branch_id,UNKNOWN_BRANCH_ID],"test_group_4",group_id)
        self.assertFalse(self.branches.update_branch_group(USER_NAME,PROJECT_NAME,branch_group_4))
        # update group
        branch_id3 = self.branches.create_branch(USER_NAME,PROJECT_NAME,NODE3_ID)
        branch_group_5 = BranchGroup([branch_id,branch_id2,branch_id3],"test_group_5",group_id)
        self.assertTrue(self.branches.update_branch_group(USER_NAME,PROJECT_NAME,branch_group_5))
        # check if the group was updated correctly
        group_content = self.branches.get_branch_group(USER_NAME,PROJECT_NAME,group_id)
        self.assertIsNotNone(group_content)
        self.assertEqual(len(group_content.branch_ids), 3)
        self.assertIn(branch_id, group_content.branch_ids)
        self.assertIn(branch_id2, group_content.branch_ids)
        self.assertIn(branch_id3, group_content.branch_ids)
        self.assertEqual(group_content.group_id, group_id)
        self.assertEqual(group_content.description, "test_group_5")