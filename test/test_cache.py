import unittest
import time
from goosvc.core.nodes import GoosvcNode
from goosvc.goosvc import Goosvc

USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_cache"
TEST_TYPE1 = "test-type-1"

class TestCache(unittest.TestCase):

    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
        self.nodes = self.gvc.core.nodes
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)
    
    def test_get_common_parent(self):
        # create linear history with 100 nodes
        node_count = 100 
        branch_id_1 = self.add_nodes(node_count)

        # read a path once
        time_start_ns = time.time_ns() 
        path = self.nodes.get_path(USER_NAME, PROJECT_NAME, branch_id_1)
        self.assertEqual(len(path), node_count+1)
        time_end_ns = time.time_ns()
        single_path_time = time_end_ns - time_start_ns
        # print("Time taken to get path once:", single_path_time)

        # create another linear history with 100 nodes
        node_count = 100 
        branch_id_2 = self.add_nodes(node_count)
        
        # retrieve same path 100 times
        time_start_ns = time.time_ns() 
        repetitions = 1000 
        for i in range(repetitions):
            path = self.nodes.get_path(USER_NAME, PROJECT_NAME, branch_id_2)
            self.assertEqual(len(path), node_count+1)
        time_end_ns = time.time_ns() 

        multiple_path_time = time_end_ns - time_start_ns
        cache_read_time = multiple_path_time - single_path_time
        cache_read_time_per_path = cache_read_time / repetitions

        self.assertLess(cache_read_time_per_path, single_path_time)

        # print("Time taken to get path",repetitions,"times:", multiple_path_time)
        # print("Cache read time:", cache_read_time)
        # print("Cache read time per path:", cache_read_time_per_path)
        # print("total ratio:", multiple_path_time/single_path_time)
        # print("cache read ratio per path:", cache_read_time_per_path/single_path_time)

        # Time taken to get path once: 44050300
        # Time taken to get path 1000 times: 157713400
        # Cache read time: 113663100
        # Cache read time per path: 113663.1
        # total ratio: 3.580302517803511
        # cache read ratio per path: 0.002580302517803511

    def add_nodes(self, count):
        node = GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 0")
        branch_id, node_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node)
        for i in range(count):
            node = GoosvcNode(TEST_TYPE1, branch_id, USER_NAME, "test content " + str(i+1))
            self.gvc.add_node(USER_NAME,PROJECT_NAME,node)
        return branch_id