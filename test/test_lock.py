import unittest
import time
from goosvc.core.nodes import GoosvcNode
import goosvc.core.common as common
from goosvc.goosvc import Goosvc
from threading import Thread
from goosvc.core.exceptions import GoosvcException

USER_NAME = "test_user"
USER_NAME2 = "test_user2"
PROJECT_NAME = "unittest_test_lock"
PROJECT_NAME2 = "unittest_test_lock2"
PROJECT_NAME3 = "unittest_test_lock3"
TEST_TYPE1 = "test-type-1"

class TestLock(unittest.TestCase):

    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.nodes = self.gvc.core.nodes
        self.branches = self.gvc.core.branches
        self.project = self.gvc.core.projects
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
        self.gvc.create_project(USER_NAME, PROJECT_NAME2)
        self.gvc.create_project(USER_NAME2, PROJECT_NAME3)
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)
        self.gvc.delete_project(USER_NAME, PROJECT_NAME2)
        self.gvc.delete_project(USER_NAME2, PROJECT_NAME3)
    
    def test_simultaneous_add(self):
        node = GoosvcNode(TEST_TYPE1, None, USER_NAME, "first node")
        branch_id, node_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node)
        t1 = Thread(target = self.write_nodes, args=(100,branch_id, 1))
        t2 = Thread(target = self.write_nodes, args=(100,branch_id, 2))
        t1.start()
        t2.start()
        # print("waiting for threads to finish")
        t1.join()
        t2.join()
        # print("analyzing")
        path = self.nodes.get_path(USER_NAME, PROJECT_NAME, branch_id)
        nodes = self.nodes.get_nodes(USER_NAME, PROJECT_NAME)
        branches = self.branches.get_branches(USER_NAME, PROJECT_NAME)
        # for node in path:
        #     print(node.content, node.version)
        self.assertEqual(len(nodes), len(path))
        self.assertEqual(len(branches), 1)
        self.assertEqual(path[0].version, len(nodes))

    def test_simultaneous_add_read(self):
        node = GoosvcNode(TEST_TYPE1, None, USER_NAME, "first node")
        branch_id, node_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node)
        t1 = Thread(target = self.write_nodes, args=(100,branch_id, 1))
        t2 = Thread(target = self.write_nodes, args=(100,branch_id, 2))
        t3 = Thread(target = self.get_branch_head, args=(1000,branch_id, 3))
        t4 = Thread(target = self.get_branch_head, args=(1000,branch_id, 4))
        t5 = Thread(target = self.get_path, args=(100,branch_id, 5))
        t1.start()
        t2.start()
        t3.start()
        t4.start()
        t5.start()
        t1.join()   
        t2.join()
        t3.join()
        t4.join()
        t5.join()

    def test_simultaneous_read(self):
        node = GoosvcNode(TEST_TYPE1, None, USER_NAME, "first node")
        branch_id, node_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node)
        t1 = Thread(target = self.read_node, args=(10000,node_id, 1))
        t2 = Thread(target = self.read_node, args=(10000,node_id, 2))
        t3 = Thread(target = self.read_node, args=(10000,node_id, 3))
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()

    def test_lock_all_projects(self):
        self.project.lock_project(USER_NAME, PROJECT_NAME)
        t1 = Thread(target = self.project.lock_all_projects, args=())
        t1.start()
        time.sleep(3)
        self.project.release_project(USER_NAME, PROJECT_NAME)
        t1.join()
        self.project.release_all_projects() 
    
    def test_lock_all_projects_and_write(self):
        # lock all projects
        self.project.lock_all_projects()
        # try to add a node to a locked project (should fail). 
        # write will wait for DEFAULT_PROJECT_LOCK_TIMEOUT (10 seconds) and then fail
        node = GoosvcNode(TEST_TYPE1, None, USER_NAME, "first node")
        self.assertRaises(GoosvcException, self.gvc.add_node, USER_NAME, PROJECT_NAME, node)
        # release all projects
        self.project.release_all_projects()
        # try to add the node again (should succeed)
        node = GoosvcNode(TEST_TYPE1, None, USER_NAME, "first node")
        branch_id, node_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node)
        self.assertIsNotNone(branch_id)
        self.assertIsNotNone(node_id)
    
    def write_nodes(self, count, branch_id, thread_id):
        # print("writing nodes in thread",thread_id)
        for i in range(count):
            node = GoosvcNode(TEST_TYPE1, branch_id, USER_NAME, "thread " + str(thread_id) + " node " + str(i+1))
            branch_id_add, node_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node)
            if branch_id_add == None:
                print("failed to add node",(i+1),"in thread",thread_id)  
        # print("finished writing nodes in thread",thread_id)

    def read_node(self, count, node_id, thread_id):
        # print("reading nodes in thread",thread_id)
        for i in range(count):
            nodes = self.nodes.get_node(USER_NAME, PROJECT_NAME, node_id)
            if nodes == None:
                print("failed to get nodes in thread",thread_id)
            self.assertEqual(nodes.node_id, node_id)
        # print("finished reading nodes in thread",thread_id)
    
    def get_path(self, count, branch_id, thread_id):
        # print("getting path in thread",thread_id)
        path_length = 0
        for i in range(count):
            path = self.nodes.get_path(USER_NAME, PROJECT_NAME, branch_id)
            self.assertIsNotNone(path)
            self.assertTrue(len(path) >= path_length)
            path_length = len(path)
            if path == None:
                print("Error: failed to get path in thread",thread_id)
            time.sleep(0.01)
        # print("finished getting path in thread",thread_id)

    def get_branch_head(self, count, branch_id, thread_id):
        # print("getting branch head in thread",thread_id)
        for i in range(count):
            branch_head = self.branches.get_branch_head(USER_NAME, PROJECT_NAME, branch_id)
            # check if branch head is valid
            self.assertIsNotNone(branch_head)
            if branch_head == None:
                print("Error: failed to get branch head in thread",thread_id)
            id_valid = common.is_id_valid(branch_head)
            self.assertTrue(id_valid)
            if not id_valid:
                print("Error: invalid branch head in thread",thread_id,":",branch_head)
            time.sleep(0.001)
        # print("finished getting branch head in thread",thread_id)
