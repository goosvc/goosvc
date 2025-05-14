import unittest
from goosvc.core import  nodes
from goosvc.goosvc import Goosvc
import time
from goosvc.core.exceptions import GoosvcException

USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_nodes"
TEST_TYPE1 = "test-type-1"
TEST_TYPE2 = "test-type-2"

class TestNodes(unittest.TestCase):

    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
        self.branches = self.gvc.core.branches
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)

    # Test null -> node1
    def test_add_first_node(self):
        heads_before = self.gvc.get_heads(USER_NAME,PROJECT_NAME)
        node1 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id, node_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        self.assertIsNotNone(branch_id)
        # check if the node is in the heads
        node1_id = self.branches.get_branch_head(USER_NAME,PROJECT_NAME,branch_id)
        heads_after = self.gvc.get_heads(USER_NAME,PROJECT_NAME)
        self.assertIsNotNone(heads_after)
        self.assertEqual(len(heads_after), len(heads_before) + 1)
        self.assertIn(node1_id, heads_after)
        # check if the node was created correctly
        node1_read = self.gvc.get_node(USER_NAME,PROJECT_NAME,node1_id)
        self.assertTrue(type(node1_read) is nodes.GoosvcNode)
        assert node1_read.type == TEST_TYPE1
        assert node1_read.parent_id == None
        assert node1_read.author == USER_NAME
        assert node1_read.content == "test content 1"
        assert node1_read.node_id == node1_id
        assert node1_read.version == 1
        # check if the path is correct
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,node1_id)
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 1)
        assert path[0].parent_id == None

    # Test null -> node1 -> node2 (use node id as parent)
    def test_add_two_consecutive_nodes(self):
        node1 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch1_id, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        heads_after_1 = self.gvc.get_heads(USER_NAME,PROJECT_NAME)
        node2 = nodes.GoosvcNode(TEST_TYPE1, node1_id, USER_NAME, "test content 2")
        branch2_id, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        assert branch2_id == branch1_id
        self.assertIsNotNone(node2_id)
        #  check if head was updated
        heads_after_2 = self.gvc.get_heads(USER_NAME,PROJECT_NAME)
        self.assertIsNotNone(heads_after_2)
        self.assertEqual(len(heads_after_2), len(heads_after_1))
        self.assertIn(node2_id, heads_after_2)
        self.assertNotIn(node1_id, heads_after_2)
        # check if the node was created correctly
        node2_read = self.gvc.get_node(USER_NAME,PROJECT_NAME,node2_id)
        self.assertTrue(type(node2_read) is nodes.GoosvcNode)
        assert node2_read.type == TEST_TYPE1
        assert node2_read.parent_id == node1_id
        assert node2_read.author == USER_NAME
        assert node2_read.content == "test content 2"
        assert node2_read.node_id == node2_id
        assert node2_read.version == 2
        # check if the path is correct
        path_node2 = self.gvc.get_path(USER_NAME,PROJECT_NAME,node2_id)
        self.assertEqual(len(path_node2), 2)
        path_node1 = self.gvc.get_path(USER_NAME,PROJECT_NAME,node1_id)
        self.assertEqual(len(path_node1), 1)

    # Test null -> node1 -> node2 (use branch id as parent)
    def test_add_two_consecutive_nodes(self):
        node1 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch1_id, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        heads_after_1 = self.gvc.get_heads(USER_NAME,PROJECT_NAME)
        node2 = nodes.GoosvcNode(TEST_TYPE1, branch1_id, USER_NAME, "test content 2") # use branch id as parent
        branch2_id, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2) 
        assert branch2_id == branch1_id
        self.assertIsNotNone(node2_id)
        #  check if head was updated
        heads_after_2 = self.gvc.get_heads(USER_NAME,PROJECT_NAME)
        self.assertIsNotNone(heads_after_2)
        self.assertEqual(len(heads_after_2), len(heads_after_1))
        self.assertIn(node2_id, heads_after_2)
        self.assertNotIn(node1_id, heads_after_2)
        # check if the node was created correctly
        node2_read = self.gvc.get_node(USER_NAME,PROJECT_NAME,node2_id)
        self.assertTrue(type(node2_read) is nodes.GoosvcNode)
        assert node2_read.type == TEST_TYPE1
        assert node2_read.parent_id == node1_id
        assert node2_read.author == USER_NAME
        assert node2_read.content == "test content 2"
        assert node2_read.node_id == node2_id
        assert node2_read.version == 2
        # check if the path is correct
        path_node2 = self.gvc.get_path(USER_NAME,PROJECT_NAME,node2_id)
        self.assertEqual(len(path_node2), 2)
        path_node1 = self.gvc.get_path(USER_NAME,PROJECT_NAME,node1_id)
        self.assertEqual(len(path_node1), 1)


    # Test null -> node1 -> node2
    #                    -> node3
    def test_branching(self):
        node1 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch1_id, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        node2 = nodes.GoosvcNode(TEST_TYPE1, branch1_id, USER_NAME, "test content 2") # add to the same branch
        branch2_id, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        node3 = nodes.GoosvcNode(TEST_TYPE1, node1_id, USER_NAME, "test content 3") # this is a branch
        branch3_id, node3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)
        # check if the branches are correct
        assert branch2_id == branch1_id
        assert branch3_id != branch1_id
        # check if head was updated
        heads_after = self.gvc.get_heads(USER_NAME,PROJECT_NAME)
        self.assertIsNotNone(heads_after)
        self.assertEqual(len(heads_after), 2)
        self.assertIn(node2_id, heads_after)
        self.assertIn(node3_id, heads_after)
        self.assertNotIn(node1_id, heads_after)
        # check if the nodes were created correctly
        node2_read = self.gvc.get_node(USER_NAME,PROJECT_NAME,node2_id)
        self.assertTrue(type(node2_read) is nodes.GoosvcNode)
        assert node2_read.type == TEST_TYPE1
        assert node2_read.parent_id == node1_id
        assert node2_read.author == USER_NAME
        assert node2_read.content == "test content 2"
        assert node2_read.node_id == node2_id
        assert node2_read.version == 2
        node3_read = self.gvc.get_node(USER_NAME,PROJECT_NAME,node3_id)
        self.assertTrue(type(node3_read) is nodes.GoosvcNode)
        assert node3_read.type == TEST_TYPE1
        assert node3_read.parent_id == node1_id
        assert node3_read.author == USER_NAME
        assert node3_read.content == "test content 3"
        assert node3_read.node_id == node3_id
        assert node2_read.version == 2
        # check if the path is correct
        path_node2 = self.gvc.get_path(USER_NAME,PROJECT_NAME,node2_id)
        self.assertEqual(len(path_node2), 2)
        path_node3 = self.gvc.get_path(USER_NAME,PROJECT_NAME,node3_id)
        self.assertEqual(len(path_node3), 2)

    def test_timestamp(self):
        node1 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch1_id, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        time.sleep(2)
        node2 = nodes.GoosvcNode(TEST_TYPE1, branch1_id, USER_NAME, "test content 2")
        branch2_id, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        # check if the timestamp is correct
        node1_read = self.gvc.get_node(USER_NAME,PROJECT_NAME,node1_id)
        node2_read = self.gvc.get_node(USER_NAME,PROJECT_NAME,node2_id)
        delta = node2_read.timestamp - node1_read.timestamp
        assert delta > 1

    def test_get_path(self):
        node1 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        node2 = nodes.GoosvcNode(TEST_TYPE2, branch_id, USER_NAME, "test content 2")
        branch_id, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        node3 = nodes.GoosvcNode(TEST_TYPE1, branch_id, USER_NAME, "test content 3")
        branch_id, node3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)
        node4 = nodes.GoosvcNode(TEST_TYPE2, branch_id, USER_NAME, "test content 4")
        branch_id, node4_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node4)
        node5 = nodes.GoosvcNode(TEST_TYPE1, branch_id, USER_NAME, "test content 5")
        branch_id, node5_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node5) 
        # all nodes from last node
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,node5_id)
        self.assertEqual(len(path), 5)
        # all nodes from branch head
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,branch_id)
        self.assertEqual(len(path), 5)
        # all nodes of type 1
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,node5_id,TEST_TYPE1)
        self.assertEqual(len(path), 3)
        # all nodes of type 2
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,node5_id,TEST_TYPE2)
        self.assertEqual(len(path), 2)
        # all nodes from branch head to node2 (exclusive)
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,branch_id,[],node2_id)
        self.assertEqual(len(path), 3)
        # all nodes from branch head to node2 (exclusive) of type 1
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,branch_id,TEST_TYPE1,node2_id)
        self.assertEqual(len(path), 2)
        # all nodes from node4 to node1 (exclusive)
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,node4_id,[],node1_id)
        self.assertEqual(len(path), 3)
        # all nodes from node4 to node1 (exclusive) of type 2
        path = self.gvc.get_path(USER_NAME,PROJECT_NAME,node4_id,TEST_TYPE2,node1_id)
        self.assertEqual(len(path), 2)

    def test_invalid_parent(self):
        node1 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        invalid_branch_id = branch_id + 'A'
        node2 = nodes.GoosvcNode(TEST_TYPE2, invalid_branch_id, USER_NAME, "test content 2")
        with self.assertRaises(GoosvcException) as context:
            branch_id, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        self.assertEqual(context.exception.code, "1029")
        invalid_node_id = node1_id + 'A'
        node3 = nodes.GoosvcNode(TEST_TYPE1, invalid_node_id, USER_NAME, "test content 3")
        with self.assertRaises(GoosvcException) as context:
            branch_id, node3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)
        self.assertEqual(context.exception.code, "1029")




    
