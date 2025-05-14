import unittest
import os
from goosvc.core.nodes import GoosvcNode
from goosvc.core.artifacts import StoreFileArtifact
from goosvc.core.merge import MergeNodeContent
from goosvc.core.stages import GoosvcStage
from goosvc.goosvc import Goosvc
from goosvc.core import chats
from goosvc.core.chats import GoosvcChat
from goosvc.core.messages import GoosvcMessage

USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_merge"
TEST_TYPE1 = "test-type-1"

FILE1_INPUT_NAME = "figure1.png"
FILE2_INPUT_NAME = "figure2.png"
FILE3_INPUT_NAME = "figure3.png"
FILE4_INPUT_NAME = "figure4.png"
FILE1_OUTPUT_NAME = "figure_1.png"
FILE2_OUTPUT_NAME = "figure_2.png"
FILE3_OUTPUT_NAME = "figure_3.png"
FILE4_OUTPUT_NAME = "figure_4.png"
OUTPUT_SUB_FOLDER = "figures_top"
OUTPUT_SUB_FOLDER2 = "figures_bottom"
MEDIA_TYPE = "image/png"
CHAT1_NAME = "Chat 1"

class TestMerge(unittest.TestCase):

    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
        self.merge = self.gvc.core.merge
        self.branches = self.gvc.core.branches
        self.stages = self.gvc.core.stages
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)
    
    # node1 -> node2 -> node3
    #                -> node4 -> node5
    #       -> node6
    def test_get_common_parent(self):
        node1 = GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id1, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        node2 = GoosvcNode(TEST_TYPE1, branch_id1, USER_NAME, "test content 2")
        branch_id1, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        node3 = GoosvcNode(TEST_TYPE1, branch_id1, USER_NAME, "test content 3")
        branch_id1, node3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)
        node4 = GoosvcNode(TEST_TYPE1, node2_id, USER_NAME, "test content 4")
        branch_id2, node4_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node4)
        node5 = GoosvcNode(TEST_TYPE1, branch_id2, USER_NAME, "test content 5")
        branch_id2, node5_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node5)
        node6 = GoosvcNode(TEST_TYPE1, node1_id, USER_NAME, "test content 6")
        branch_id3, node6_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node6)
        # get common parent of 2 nodes
        parent_id = self.merge.get_common_parent(USER_NAME, PROJECT_NAME, [node3_id, node5_id])
        assert parent_id == node2_id
        parent_id = self.merge.get_common_parent(USER_NAME, PROJECT_NAME, [node3_id, node4_id])
        assert parent_id == node2_id
        parent_id = self.merge.get_common_parent(USER_NAME, PROJECT_NAME, [node4_id, node5_id])
        assert parent_id == node4_id
        parent_id = self.merge.get_common_parent(USER_NAME, PROJECT_NAME, [node1_id, node5_id])
        assert parent_id == node1_id
        parent_id = self.merge.get_common_parent(USER_NAME, PROJECT_NAME, [node6_id, node5_id])
        assert parent_id == node1_id
        parent_id = self.merge.get_common_parent(USER_NAME, PROJECT_NAME, [node4_id, node5_id, node3_id])   
        assert parent_id == node2_id
        parent_id = self.merge.get_common_parent(USER_NAME, PROJECT_NAME, [node4_id, node5_id, node3_id, node6_id])   
        assert parent_id == node1_id

    def test_get_merge_conflicts(self):
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, _, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # add 3 artifacts in same branch
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file_1 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_1, MEDIA_TYPE)
        branch_id, node_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        input_file_2 = os.path.join(input_folder, FILE2_INPUT_NAME)
        artifact2 = StoreFileArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_2, MEDIA_TYPE)
        branch_id, node2_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact2)
        input_file_3 = os.path.join(input_folder, FILE3_INPUT_NAME)
        artifact3 = StoreFileArtifact(USER_NAME, FILE3_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_3, MEDIA_TYPE)
        branch_id, node3_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact3)
        # create 3 branches
        node1 = GoosvcNode(TEST_TYPE1, node3_id, USER_NAME, "test content 1")
        branch_id1, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        node2 = GoosvcNode(TEST_TYPE1, node3_id, USER_NAME, "test content 2")
        branch_id2, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        node3 = GoosvcNode(TEST_TYPE1, node3_id, USER_NAME, "test content 3")
        branch_id3, node3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)
        # assert no merge conflicts
        common_parent_id = self.merge.get_common_parent(USER_NAME, PROJECT_NAME, [node1_id, node2_id, node3_id])
        merge_conflicts = self.merge.get_merge_conflicts(USER_NAME, PROJECT_NAME, common_parent_id, [node1_id, node2_id, node3_id])
        # print("Conflicts:",merge_conflicts)
        self.assertEqual(len(merge_conflicts), 0)
        # modify artifact 1 in all three branches
        input_file_4 = os.path.join(input_folder, FILE2_INPUT_NAME)
        artifact1a = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_4, MEDIA_TYPE)
        branch_id, node4_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id1, chat_id, artifact1a)
        input_file_5 = os.path.join(input_folder, FILE3_INPUT_NAME)
        artifact1b = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_5, MEDIA_TYPE)
        branch_id, node5_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id2, chat_id, artifact1b)
        input_file_6 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1c = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_6, MEDIA_TYPE)
        branch_id, node6_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id3, chat_id, artifact1c)
        # assert merge conflicts
        merge_conflicts = self.merge.get_merge_conflicts(USER_NAME, PROJECT_NAME, common_parent_id, [node4_id, node5_id, node6_id])
        self.assertEqual(len(merge_conflicts), 1)
        artifact1_filename = os.path.join(OUTPUT_SUB_FOLDER, FILE1_OUTPUT_NAME)
        self.assertEqual(len(merge_conflicts[artifact1_filename]), 3)
        self.assertIn(node4_id, merge_conflicts[artifact1_filename])  
        self.assertIn(node5_id, merge_conflicts[artifact1_filename])
        self.assertIn(node6_id, merge_conflicts[artifact1_filename]) 
        # modify artifact 2 in two branches 
        input_file_7 = os.path.join(input_folder, FILE3_INPUT_NAME)
        artifact2a = StoreFileArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_7, MEDIA_TYPE)
        branch_id, node7_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id1, chat_id, artifact2a)
        input_file_8 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact2b = StoreFileArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_8, MEDIA_TYPE)
        branch_id, node8_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id2, chat_id, artifact2b)
        # assert merge conflicts
        merge_conflicts = self.merge.get_merge_conflicts(USER_NAME, PROJECT_NAME, common_parent_id, [node7_id, node8_id, node6_id])
        self.assertEqual(len(merge_conflicts), 2)
        artifact2_filename = os.path.join(OUTPUT_SUB_FOLDER, FILE2_OUTPUT_NAME)
        self.assertEqual(len(merge_conflicts[artifact2_filename]), 2)
        self.assertIn(node7_id, merge_conflicts[artifact2_filename])
        self.assertIn(node8_id, merge_conflicts[artifact2_filename])
        # modify artifact 3 in one branche
        input_file_9 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact3a = StoreFileArtifact(USER_NAME, FILE3_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_9, MEDIA_TYPE)
        branch_id, node9_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id1, chat_id, artifact3a)
        # assert merge conflicts have not changed
        merge_conflicts = self.merge.get_merge_conflicts(USER_NAME, PROJECT_NAME, common_parent_id, [node7_id, node8_id, node6_id])
        self.assertEqual(len(merge_conflicts), 2)

    def test_merge(self):
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, _, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # add 3 artifacts in same branch
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file_1 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_1, MEDIA_TYPE)
        branch_id, node_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        input_file_2 = os.path.join(input_folder, FILE2_INPUT_NAME)
        artifact2 = StoreFileArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_2, MEDIA_TYPE)
        branch_id, node2_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact2)
        input_file_3 = os.path.join(input_folder, FILE3_INPUT_NAME)
        artifact3 = StoreFileArtifact(USER_NAME, FILE3_OUTPUT_NAME, OUTPUT_SUB_FOLDER, input_file_3, MEDIA_TYPE)
        branch_id, node3_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact3)
        # create 3 branches
        node1 = GoosvcNode(TEST_TYPE1, node3_id, USER_NAME, "test content 1")
        branch_id1, node1_b1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        node2 = GoosvcNode(TEST_TYPE1, node3_id, USER_NAME, "test content 2")
        branch_id2, node1_b2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        node3 = GoosvcNode(TEST_TYPE1, node3_id, USER_NAME, "test content 3")
        branch_id3, node1_b3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)
        # get branches before merge
        branches = self.branches.get_branches(USER_NAME, PROJECT_NAME)
        self.assertEqual(len(branches), 3)
        # merge 3 branches
        merge_branch_id, merge_head_node_id = self.merge.merge(USER_NAME, PROJECT_NAME, USER_NAME, [node1_b1_id, branch_id2, node1_b3_id])
        self.assertIsNotNone(merge_branch_id)
        # get branches before merge
        branches = self.branches.get_branches(USER_NAME, PROJECT_NAME)
        self.assertEqual(len(branches), 4)
        # check last node in merge branch (end merge node)
        node = self.gvc.get_node(USER_NAME, PROJECT_NAME, merge_head_node_id)
        self.assertEqual(node.type, "merge")
        self.assertEqual(node.version, 8)
        merge_node_content = MergeNodeContent(**node.content)
        self.assertEqual(merge_node_content.common_parent_id, node3_id)
        self.assertEqual(merge_node_content.head_ids, [node1_b1_id, node1_b2_id, node1_b3_id])
        # check node_id_map in merge end node
        node_id_dict = merge_node_content.node_id_dict
        self.assertEqual(len(node_id_dict), 3) # 3 nodes 
        for new_node_id, ref_node_id in node_id_dict.items():
            self.assertNotEqual(new_node_id, ref_node_id)
            new_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, new_node_id)
            self.assertIsNotNone(new_node)
            ref_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, ref_node_id)
            self.assertIsNotNone(ref_node)
            self.assertEqual(new_node.content, ref_node.content)
        # check path of merge branch
        path = self.gvc.get_path(USER_NAME, PROJECT_NAME, merge_head_node_id)
        self.assertEqual(len(path), 8)
        self.assertEqual(path[0].type, "merge")
        self.assertEqual(path[1].content, "test content 3")
        self.assertEqual(path[1].type, "test-type-1")
        self.assertEqual(path[2].content, "test content 2")
        self.assertEqual(path[3].content, "test content 1")
       
    # node1 -> stage1-> node2 -> stage2 -> node4
    #                -> node3 ->
    # nodes 2 and 3 can be merged, nodes 3 and 4 cannot be merged
    def test_merge_with_stages(self):
        node1 = GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id1, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        stage1 = GoosvcStage(USER_NAME, "first stage", "first stage description")
        branch_id1, stage1_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, branch_id1, stage1)
        node2 = GoosvcNode(TEST_TYPE1, stage1_id, USER_NAME, "test content 2")
        branch_id1, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        node3 = GoosvcNode(TEST_TYPE1, stage1_id, USER_NAME, "test content 3") 
        branch_id2, node3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)  # branch
        stage2 = GoosvcStage(USER_NAME, "second stage", "second stage description")
        branch_id1, stage2_id = self.stages.add_stage(USER_NAME, PROJECT_NAME, node2_id, stage2)
        node4 = GoosvcNode(TEST_TYPE1, stage2_id, USER_NAME, "test content 4")
        branch_id1, node4_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node4)
        # get branches before merge
        branches = self.branches.get_branches(USER_NAME, PROJECT_NAME)
        self.assertEqual(len(branches), 2)
        # check stages before merge
        stages = self.stages.get_stage_nodes(USER_NAME, PROJECT_NAME, node4_id)
        self.assertEqual(len(stages), 2)
        stages = self.stages.get_stage_nodes(USER_NAME, PROJECT_NAME, node3_id)
        self.assertEqual(len(stages), 1)
        # merge 2 and 4
        self.assertEqual(self.merge.merge(USER_NAME, PROJECT_NAME, USER_NAME, [node2_id, node4_id]), (None, None))
        # merge 2 and 3
        merge_branch_id, merge_head_node_id = self.merge.merge(USER_NAME, PROJECT_NAME, USER_NAME, [node2_id, node3_id])
        self.assertIsNotNone(merge_branch_id)
        # get branches after merge
        branches = self.branches.get_branches(USER_NAME, PROJECT_NAME)
        self.assertEqual(len(branches), 3)
        # check path of merge branch: end-merge, node3, node2, start-merge, stage1, node1
        path = self.gvc.get_path(USER_NAME, PROJECT_NAME, merge_head_node_id)
        self.assertEqual(len(path), 5)
        self.assertEqual(path[0].type, "merge")
        self.assertEqual(path[1].content, "test content 3")
        self.assertEqual(path[2].content, "test content 2")
        self.assertEqual(path[3].content['stage_name'], "first stage")
        self.assertEqual(path[4].content, "test content 1")

    # when a new chat is created between common parent and merge head there are three situations:
    # a) the chat has no parent chat node
    # b) the chat has a parent chat node before the merge head
    # c) the chat has a parent chat node after the merge head
    # For a) and b) no action is needed for the chat node itself but for all attached messages the chat id must be updated.
    # For c) the chat nodes parent chat node id has to be updated. For the attached messages the chat id must be updated.
    # 
    # chat 1:  chat 1  -> message 1
    # chat a:  chat a  -> message a
    # chat b:  chat 1  -> message 1  -> chat b  -> message b
    # chat c1: chat c1 -> message c1
    # chat c2: chat c1 -> message c1 -> chat c2 -> message c2
    def test_merge_new_chat(self):
        node1 = GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id1, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        chat1 = GoosvcChat(USER_NAME, "chat 1") # first chat, no parent
        branch_id1, chat1_node_id, chat1_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id1, chat1)
        message1 = GoosvcMessage(USER_NAME, "Message before branch", "...", chat1_id)
        branch_id1, message1_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id1, message1)
        # branch for case a)
        node2 = GoosvcNode(TEST_TYPE1, message1_node_id, USER_NAME, "test content 2")
        branch_id1, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        chat_a = GoosvcChat(USER_NAME, "chat a") # second chat, no parent
        branch_id1, chat_a_node_id, chat_a_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id1, chat_a)
        message2a = GoosvcMessage(USER_NAME, "Message a", "...", chat_a_id)
        branch_id1, message2a_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id1, message2a)
        # branch for case b)
        node3 = GoosvcNode(TEST_TYPE1, message1_node_id, USER_NAME, "test content 3")
        branch_id2, node3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)
        chat_b = GoosvcChat(USER_NAME, "chat b",message1_node_id) # third chat, parent before merge head
        branch_id2, chat_b_node_id, chat_b_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id2, chat_b)
        message2b = GoosvcMessage(USER_NAME, "Message b", "...", chat_b_id)
        branch_id2, message2b_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id2, message2b)
        # branch for case c)
        node4 = GoosvcNode(TEST_TYPE1, message1_node_id, USER_NAME, "test content 4")
        branch_id3, node4_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node4)
        chat_c1 = GoosvcChat(USER_NAME, "chat c1") # fourth chat, no parent
        branch_id3, chat_c1_node_id, chat_c1_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id3, chat_c1)
        message2c1 = GoosvcMessage(USER_NAME, "Message c1", "...", chat_c1_id)
        branch_id3, message2c_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id3, message2c1)
        chat_c2 = GoosvcChat(USER_NAME, "chat c2", message2c_node_id) # fifth chat, parent after merge head
        branch_id3, chat_c2_node_id, chat_c2_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id3, chat_c2)
        message2c2 = GoosvcMessage(USER_NAME, "Message c2", "...", chat_c2_id)
        branch_id3, message2c2_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id3, message2c2)
        # check we have 3 branches
        branches = self.branches.get_branches(USER_NAME, PROJECT_NAME)
        self.assertEqual(len(branches), 3)
        # merge a), b) and c)
        merge_branch_id, merge_head_node_id = self.merge.merge(USER_NAME, PROJECT_NAME, USER_NAME, [message2a_node_id, message2b_node_id, message2c2_node_id])
        # check merge was successful
        self.assertIsNotNone(merge_branch_id)
        branches = self.branches.get_branches(USER_NAME, PROJECT_NAME)
        self.assertEqual(len(branches), 4)
        # check the number of chats
        chats = self.gvc.get_chats(USER_NAME, PROJECT_NAME, merge_branch_id)
        self.assertEqual(len(chats), 5)
        # check chat a
        chats_a = [chat for chat in chats if chat["chat_name"] == "chat a"]
        self.assertEqual(len(chats_a), 1)
        chat_a = chats_a[0]
        chat_a_message_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat_a["chat_id"], merge_branch_id)
        self.assertEqual(len(chat_a_message_nodes), 1)
        self.assertEqual(chat_a_message_nodes[0].content['request'], "Message a")
        # check chat b
        chats_b = [chat for chat in chats if chat["chat_name"] == "chat b"]
        self.assertEqual(len(chats_b), 1)
        chat_b = chats_b[0]
        chat_b_message_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat_b["chat_id"], merge_branch_id)
        self.assertEqual(len(chat_b_message_nodes), 2)
        self.assertEqual(chat_b_message_nodes[0].content['request'], "Message before branch")
        self.assertEqual(chat_b_message_nodes[1].content['request'], "Message b")
        # check chat c1
        chats_c1 = [chat for chat in chats if chat["chat_name"] == "chat c1"]
        self.assertEqual(len(chats_c1), 1)
        chat_c1 = chats_c1[0]
        chat_c1_message_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat_c1["chat_id"], merge_branch_id)
        self.assertEqual(len(chat_c1_message_nodes), 1)
        self.assertEqual(chat_c1_message_nodes[0].content['request'], "Message c1")
        # check chat c2
        chats_c2 = [chat for chat in chats if chat["chat_name"] == "chat c2"]
        self.assertEqual(len(chats_c2), 1)
        chat_c2 = chats_c2[0]
        chat_c2_message_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat_c2["chat_id"], merge_branch_id)
        self.assertEqual(len(chat_c2_message_nodes), 2)
        self.assertEqual(chat_c2_message_nodes[0].content['request'], "Message c1")
        self.assertEqual(chat_c2_message_nodes[1].content['request'], "Message c2")

    # before merge:
    # branch 1: chat 1 -> message a -> message b -> message c
    # branch 2:                     -> message d -> message e
    # merge branch:
    # branch 3: chat 1 -> message a -> message b -> message c -> chat 2 -> message d -> message e
    #                               \___________________________/
    def test_merge_chat_conflict(self):
        node1 = GoosvcNode(TEST_TYPE1, None, USER_NAME, "test content 1")
        branch_id1, node1_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node1)
        chat1 = GoosvcChat(USER_NAME, "chat 1") # first chat, no parent
        branch_id1, chat1_node_id, chat1_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id1, chat1)
        message_a = GoosvcMessage(USER_NAME, "Message a", "...", chat1_id)
        branch_id1, message_a_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id1, message_a)
        # branch 1
        node2 = GoosvcNode(TEST_TYPE1, message_a_node_id, USER_NAME, "test content 2")
        branch_id1, node2_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node2)
        message_b = GoosvcMessage(USER_NAME, "Message b", "...", chat1_id)
        branch_id1, message_b_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id1, message_b)
        message_c = GoosvcMessage(USER_NAME, "Message c", "...", chat1_id)
        branch_id1, message_c_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id1, message_c)
        # branch 2
        node3 = GoosvcNode(TEST_TYPE1, message_a_node_id, USER_NAME, "test content 3")
        branch_id2, node3_id = self.gvc.add_node(USER_NAME,PROJECT_NAME,node3)
        message_d = GoosvcMessage(USER_NAME, "Message d", "...", chat1_id)
        branch_id2, message_d_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id2, message_d)
        message_e = GoosvcMessage(USER_NAME, "Message e", "...", chat1_id)
        branch_id2, message_e_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id2, message_e)
        # merge
        merge_branch_id, merge_head_node_id = self.merge.merge(USER_NAME, PROJECT_NAME, USER_NAME, [message_c_node_id, message_e_node_id])
        # check merge was successful
        self.assertIsNotNone(merge_branch_id)
        # check the number of chats
        chats = self.gvc.get_chats(USER_NAME, PROJECT_NAME, merge_branch_id)
        self.assertEqual(len(chats), 2)
        # check chat 1
        chats_1 = [chat for chat in chats if chat["chat_name"] == "chat 1"]
        self.assertEqual(len(chats_1), 1)
        chat_1 = chats_1[0]
        chat_1_message_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat_1["chat_id"], merge_branch_id)
        self.assertEqual(len(chat_1_message_nodes), 3)
        self.assertEqual(chat_1_message_nodes[0].content['request'], "Message a")
        self.assertEqual(chat_1_message_nodes[1].content['request'], "Message b")
        self.assertEqual(chat_1_message_nodes[2].content['request'], "Message c")
        # check chat 2
        chats_2 = [chat for chat in chats if chat["chat_name"] == "chat 1."]
        self.assertEqual(len(chats_2), 1)
        chat_2 = chats_2[0]
        chat_2_message_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat_2["chat_id"], merge_branch_id)
        self.assertEqual(len(chat_2_message_nodes), 3)
        self.assertEqual(chat_2_message_nodes[0].content['request'], "Message a")
        self.assertEqual(chat_2_message_nodes[1].content['request'], "Message d")
        self.assertEqual(chat_2_message_nodes[2].content['request'], "Message e")


        


