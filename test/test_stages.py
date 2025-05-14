import unittest
from goosvc.core import  nodes
from goosvc.core.stages import GoosvcStage, StageNodeContent
from goosvc.goosvc import Goosvc
from goosvc.core.exceptions import GoosvcException

USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_stages"
TEST_TYPE1 = "test-type-1"


STAGE1_NAME = "first stage"
STAGE1_DESC = "first stage description"
STAGE2_NAME = "second stage"
STAGE2_DESC = "second stage description"
STAGE3_NAME = "third stage"
STAGE3_DESC = "third stage description"
STAGE4_NAME = "fourth stage"
STAGE4_DESC = "fourth stage description"

class TestStages(unittest.TestCase):

    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
        self.stages = self.gvc.core.stages
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)

    def test_add_stages_single_branch(self):
        node1 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        # assert no stages in new project
        stages_before = self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id)
        assert len(stages_before) == 0
        # add first stage
        stage1 = GoosvcStage(USER_NAME, STAGE1_NAME, STAGE1_DESC)
        branch_id, node_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, branch_id, stage1)
        stage1_nodes = self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id)
        assert len(stage1_nodes) == 1
        stage1_node_content = StageNodeContent(**stage1_nodes[0].content)
        assert stage1_node_content.stage_name == STAGE1_NAME
        assert stage1_node_content.stage_description == STAGE1_DESC
        # add second stage
        stage2 = GoosvcStage(USER_NAME, STAGE2_NAME, STAGE2_DESC)
        branch_id, node_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, branch_id, stage2)
        stage2_nodes = self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id)
        assert len(stage2_nodes) == 2
        stage2_node_content = StageNodeContent(**stage2_nodes[0].content)
        assert stage2_node_content.stage_name == STAGE2_NAME
        # add stage with same name as stage1
        stage3 = GoosvcStage(USER_NAME, STAGE1_NAME, STAGE1_DESC)
        self.assertRaises(GoosvcException, self.stages.add_stage, USER_NAME, PROJECT_NAME, branch_id, stage3)
        assert len(self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id)) == 2
        # add stage with same name as stage2 but different description
        stage3 = GoosvcStage(USER_NAME, STAGE2_NAME, STAGE3_DESC)
        self.assertRaises(GoosvcException, self.stages.add_stage, USER_NAME, PROJECT_NAME, branch_id, stage3)
        assert len(self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id)) == 2
        # add third stage
        stage3 = GoosvcStage(USER_NAME, STAGE3_NAME, STAGE3_DESC)
        branch_id, node_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, branch_id, stage3)
        stage3_nodes = self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id)
        assert len(stage3_nodes) == 3
        # test get_stage_names
        stage_names = self.stages.get_stage_names(USER_NAME,PROJECT_NAME,branch_id)
        assert len(stage_names) == 3
        assert STAGE1_NAME in stage_names
        assert STAGE2_NAME in stage_names
        assert STAGE3_NAME in stage_names
        # test get_stage_node
        stage_node = self.stages.get_stage_node(USER_NAME,PROJECT_NAME,branch_id,STAGE2_NAME)
        assert stage_node != None
        assert stage_node.content['stage_name'] == STAGE2_NAME
        # test stage_exists
        assert self.stages.stage_exists(USER_NAME,PROJECT_NAME,branch_id,STAGE2_NAME)
        assert not self.stages.stage_exists(USER_NAME,PROJECT_NAME,branch_id,"not a stage")

    def test_add_stages_two_branches(self):
        node0 = nodes.GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 0")
        branch_id0, node0_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node0)
        node1 = nodes.GoosvcNode(TEST_TYPE1, node0_id, USER_NAME, "test content 1")
        branch_id1, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        node2 = nodes.GoosvcNode(TEST_TYPE1, node0_id, USER_NAME, "test content 2")
        branch_id2, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        assert branch_id1 != branch_id2
        # add first stage to branch 1
        stage1 = GoosvcStage(USER_NAME, STAGE1_NAME, STAGE1_DESC)
        branch_id, node_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, branch_id1, stage1)
        stage1_nodes = self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id1)
        assert len(stage1_nodes) == 1
        # add first stage to branch 2
        stage1 = GoosvcStage(USER_NAME, STAGE1_NAME, STAGE1_DESC)
        branch_id, node_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, branch_id2, stage1)
        stage1_nodes = self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id2)
        assert len(stage1_nodes) == 1
        # add second stage to branch 1
        stage2 = GoosvcStage(USER_NAME, STAGE2_NAME, STAGE2_DESC)
        branch_id, node_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, branch_id1, stage2)
        stage2_nodes = self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id1)
        assert len(stage2_nodes) == 2
        # add second stage to branch 2
        stage2 = GoosvcStage(USER_NAME, STAGE2_NAME, STAGE2_DESC)
        branch_id, node_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, branch_id2, stage2)
        stage2_nodes = self.stages.get_stage_nodes(USER_NAME,PROJECT_NAME,branch_id2)
        assert len(stage2_nodes) == 2
 