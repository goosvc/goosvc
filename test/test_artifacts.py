import unittest
import os
import json
from dataclasses import dataclass
import dataclasses

from goosvc.goosvc import Goosvc
from goosvc.core import  nodes
from goosvc.core import chats
from goosvc.core.artifacts import StoreFileArtifact, StoreTextArtifact, ArtifactNodeContent, DeleteArtifact, RenameArtifact
from goosvc.core.exceptions import GoosvcException

USER_NAME = "test_user"
USER_NAME2 = "test_user_2"
PROJECT_NAME = "unittest_test_artifacts"

FILE1_INPUT_NAME = "figure1.png"
FILE2_INPUT_NAME = "figure2.png"
FILE3_INPUT_NAME = "figure3.png"
FILE4_INPUT_NAME = "figure4.png"
FILE1_OUTPUT_NAME = "figure_1.png"
FILE2_OUTPUT_NAME = "figure_2.png"
FILE3_OUTPUT_NAME = "figure_3.png"
OUTPUT_FOLDER = "figures_top"
MEDIA_TYPE_PNG = "image/png"
MEDIA_TYPE_TEXT = "text/plain"
MEDIA_TYPE_JSON = "application/json"
CHAT1_NAME = "Chat 1"
CHAT2_NAME = "Chat 2"
TEXT_CONTENT = "This is a test text content."
JSON_CONTENT = {"key": "value", "key2": "value2"}
TEXT_FOLDER = "texts"
TEXT_FILE_NAME = "test_text.txt"
JSON_FOLDER = "jsons"
JSON_FILE_NAME = "test_json.json"
ORIGIN1 = "user input"
ORIGIN2 = "external tool"


FIGURE1_HASH = "e7a43ea77783a1f9130c6d0e5040f01a"
FIGURE2_HASH = "4b9bbb07da97a441faa3023cd6ab1b68"

class TestArtifacts(unittest.TestCase):

    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
        self.branches = self.gvc.core.branches
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)

    def test_store_file_artifact(self):
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, chat_node_id, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # store artifact
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file, MEDIA_TYPE_PNG, None, ORIGIN1)
        branch_id, node_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        self.assertIsNotNone(node_id)
        # check if the node was created correctly
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node_id)
        self.assertTrue(type(node_read) is nodes.GoosvcNode)
        assert node_read.type == "artifact"
        assert node_read.parent_id == chat_node_id
        assert node_read.author == USER_NAME
        node_content = ArtifactNodeContent(**node_read.content)
        artifact_id = node_content.artifact_id
        assert node_content.operation == "add"
        assert node_content.filename == FILE1_OUTPUT_NAME
        assert node_content.path == OUTPUT_FOLDER
        assert node_content.filehash == FIGURE1_HASH
        assert node_content.origin == ORIGIN1
        # check if get_artifact_nodes works
        artifact_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node_id, chat_id)
        assert len(artifact_nodes) == 1
        assert artifact_nodes[0].node_id == node_id
        artifact = ArtifactNodeContent(**artifact_nodes[0].content)
        assert artifact.artifact_id == artifact_id
        assert artifact.filename == FILE1_OUTPUT_NAME
        assert artifact.path == OUTPUT_FOLDER
        assert artifact.origin == ORIGIN1
        # check if get_artifact_node works
        artifact_node = self.gvc.get_artifact_node_by_name(USER_NAME, PROJECT_NAME, node_id, chat_id, FILE2_OUTPUT_NAME, OUTPUT_FOLDER)
        assert artifact_node is None # file name is different
        artifact_node = self.gvc.get_artifact_node_by_name(USER_NAME, PROJECT_NAME, node_id, chat_id, FILE1_OUTPUT_NAME, OUTPUT_FOLDER)
        assert artifact_node.node_id == node_id
        # 2DO: check if the artifact was stored correctly

    def test_store_text_artifact(self):
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, chat_node_id, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # store artifact
        artifact1 = StoreTextArtifact(USER_NAME, TEXT_FILE_NAME, TEXT_FOLDER, TEXT_CONTENT, MEDIA_TYPE_TEXT, None, ORIGIN1)
        branch_id, _ = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        artifact2 = StoreTextArtifact(USER_NAME, JSON_FILE_NAME, JSON_FOLDER, json.dumps(JSON_CONTENT), MEDIA_TYPE_JSON, None, ORIGIN2)
        branch_id, _ = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact2)
        # check if the node was created correctly
        artifacts = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat_id)
        self.assertEqual(len(artifacts), 2)
        artifact1 = artifacts[1]
        artifact2 = artifacts[0]
        self.assertEqual(artifact1.filename, TEXT_FILE_NAME)
        self.assertEqual(artifact1.path, TEXT_FOLDER)
        self.assertEqual(artifact1.media_type, MEDIA_TYPE_TEXT)
        self.assertEqual(artifact1.origin, ORIGIN1)
        self.assertEqual(artifact2.filename, JSON_FILE_NAME)
        self.assertEqual(artifact2.path, JSON_FOLDER)
        self.assertEqual(artifact2.media_type, MEDIA_TYPE_JSON)
        self.assertEqual(artifact2.origin, ORIGIN2)
        # check if file content is correct
        artifact1_id = artifact1.artifact_id
        artifact2_id = artifact2.artifact_id
        artifact1_file = self.gvc.get_artifact_file(USER_NAME, PROJECT_NAME, artifact1_id)
        artifact2_file = self.gvc.get_artifact_file(USER_NAME, PROJECT_NAME, artifact2_id)
        with open(artifact1_file, "r") as f:
            artifact_file_content = f.read()
            self.assertEqual(artifact_file_content, TEXT_CONTENT)
        with open(artifact2_file, "r") as f:
            artifact_file_content = f.read()
            self.assertEqual(artifact_file_content, json.dumps(JSON_CONTENT))
    
    def test_update_artifact(self):
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch1_id, _, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # store artifact
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file_1 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_1, MEDIA_TYPE_PNG)
        branch1_id, node1_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch1_id, chat_id, artifact1)
        # update artifact
        input_file_2 = os.path.join(input_folder, FILE2_INPUT_NAME)
        artifact2 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_2, MEDIA_TYPE_PNG)
        branch2_id, node2_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch1_id, chat_id, artifact2)
        # check if the branch is the same
        assert branch2_id == branch1_id
        # check if the node was created correctly
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node2_id)
        self.assertTrue(type(node_read) is nodes.GoosvcNode)
        assert node_read.type == "artifact"
        assert node_read.parent_id == node1_id
        assert node_read.author == USER_NAME
        node_content = ArtifactNodeContent(**node_read.content)
        artifact_id = node_content.artifact_id
        assert node_content.operation == "update"
        assert node_content.filename == FILE1_OUTPUT_NAME
        assert node_content.path == OUTPUT_FOLDER
        assert node_content.filehash == FIGURE2_HASH
        # check if get_artifact_nodes works
        artifact_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node2_id, chat_id)
        assert len(artifact_nodes) == 1
        assert artifact_nodes[0].node_id == node2_id
        artifact = ArtifactNodeContent(**artifact_nodes[0].content)
        assert artifact.artifact_id == artifact_id
        assert artifact.filename == FILE1_OUTPUT_NAME
        assert artifact.path == OUTPUT_FOLDER
        # check if all versions of the artifact are available
        all_versions = self.gvc.get_all_artifact_versions(USER_NAME, PROJECT_NAME, branch2_id, node2_id)
        assert len(all_versions) == 2
        assert all_versions[0].node_id == node1_id
        assert all_versions[0].version == 2
        assert all_versions[0].content['operation'] == "add"
        assert all_versions[1].node_id == node2_id
        assert all_versions[1].version == 3
        assert all_versions[1].content['operation'] == "update"
        # 2DO: check if the artifact was stored correctly

    def test_delete_artifact(self):
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch1_id, _, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # store artifact
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file, MEDIA_TYPE_PNG)
        branch1_id, node1_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch1_id, chat_id, artifact1)
        # delete artifact
        artifact2 = DeleteArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER)
        branch2_id, node2_id = self.gvc.delete_artifact(USER_NAME, PROJECT_NAME, node1_id, chat_id, artifact2)
        # check if the node was created correctly
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node2_id)
        self.assertTrue(type(node_read) is nodes.GoosvcNode)
        assert node_read.type == "artifact"
        assert node_read.parent_id == node1_id
        assert node_read.author == USER_NAME
        node_content = ArtifactNodeContent(**node_read.content)
        assert node_content.operation == "delete"
        assert node_content.filename == FILE1_OUTPUT_NAME
        assert node_content.path == OUTPUT_FOLDER
        # check if get_artifact_nodes works
        artifact_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node2_id, chat_id)
        assert len(artifact_nodes) == 1
        artifacts = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, node2_id, chat_id)
        assert len(artifacts) == 0

    def test_rename_artifact(self):
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch1_id, _, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # store artifact
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file_1 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_1, MEDIA_TYPE_PNG)
        branch1_id, node1_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch1_id, chat_id, artifact1)
        # get artifact id
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node1_id)
        self.assertTrue(type(node_read) is nodes.GoosvcNode)
        node_content = ArtifactNodeContent(**node_read.content)
        artifact_id = node_content.artifact_id
        # rename artifact
        artifact1_new = RenameArtifact(USER_NAME2, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, "new_name.png", "new_path")
        branch2_id, node2_id = self.gvc.rename_artifact(USER_NAME, PROJECT_NAME, branch1_id, chat_id, artifact1_new)
        # check if the node was created correctly
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node2_id)
        self.assertTrue(type(node_read) is nodes.GoosvcNode)
        self.assertEqual(node_read.type, "artifact")
        self.assertEqual(node_read.author, USER_NAME2)
        node_content = ArtifactNodeContent(**node_read.content)
        self.assertEqual(artifact_id, node_content.artifact_id) # same artifact id
        self.assertEqual(node_content.operation, "add")
        self.assertEqual(node_content.filename, "new_name.png")
        self.assertEqual(node_content.path, "new_path")
        # check if artifact under the old name is deleted
        artifacts = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, node1_id, chat_id)
        self.assertEqual(len(artifacts), 1)
        artifact_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node2_id, chat_id)
        self.assertEqual(len(artifact_nodes), 2) # one with operation "add" and one with operation "delete"
        
    
    # | figure_1.png | figure_2.png | figure_3.png | Version | Artifacts
    # |--------------|--------------|--------------|---------|-----------|
    # | add          |              |              | 1       | 1         | add
    # |              |              | add          | 2       | 1, 2      | add 
    # |              | add          |              | 3       | 1, 2, 3   | add 
    # |              | update       |              | 4       | 1, 2, 3   | update after add
    # | delete       |              |              | 5       | 2, 3      | delete after add
    # |              | delete       |              | 6       | 3,        | delete after update
    # | add          |              |              | 7       | 1, 3      | add after delete
    
    def test_get_artifact_nodes(self):
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file_1 = os.path.join(input_folder, FILE1_INPUT_NAME)
        input_file_2 = os.path.join(input_folder, FILE2_INPUT_NAME)
        input_file_3 = os.path.join(input_folder, FILE1_INPUT_NAME)
        input_file_4 = os.path.join(input_folder, FILE2_INPUT_NAME)
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, _, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # Version 1
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_1, MEDIA_TYPE_PNG)
        branch_id, node1_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        # Version 2
        artifact2 = StoreFileArtifact(USER_NAME, FILE3_OUTPUT_NAME, OUTPUT_FOLDER, input_file_3, MEDIA_TYPE_PNG)
        branch_id, node2_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact2)
        # Version 3
        artifact3 = StoreFileArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_FOLDER, input_file_2, MEDIA_TYPE_PNG)
        branch_id, node3_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact3)
        # Version 4
        artifact4 = StoreFileArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_FOLDER, input_file_4, MEDIA_TYPE_PNG)
        branch_id, node4_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact4)
        # Version 5
        artifact5 = DeleteArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER)
        branch_id, node5_id = self.gvc.delete_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact5)
        # Version 6
        artifact6 = DeleteArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_FOLDER)
        branch_id, node6_id = self.gvc.delete_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact6)
        # Version 7
        artifact7 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_1, MEDIA_TYPE_PNG)
        branch_id, node7_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact7)
        # check get all artifact at different versions
        v3_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node3_id, chat_id)
        v3_artifacts = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, node3_id, chat_id)
        assert len(v3_nodes) == 3
        assert len(v3_artifacts) == 3
        v4_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node4_id, chat_id)
        v4_artifacts = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, node4_id, chat_id)
        assert len(v4_nodes) == 3
        assert len(v4_artifacts) == 3
        v5_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node5_id, chat_id)
        v5_artifacts = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, node5_id, chat_id)
        assert len(v5_nodes) == 3
        assert len(v5_artifacts) == 2
        v6_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node6_id, chat_id)
        v6_artifacts = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, node6_id, chat_id)
        assert len(v6_nodes) == 3
        assert len(v6_artifacts) == 1
        v7_nodes = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, node7_id, chat_id)
        v7_artifacts = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, node7_id, chat_id)
        assert len(v7_nodes) == 3
        assert len(v7_artifacts) == 2
        # check get diff artifacts for different ranges
        v7_to_v5 = self.gvc.get_diff_artifact_nodes(USER_NAME, PROJECT_NAME, node7_id, node5_id)
        assert len(v7_to_v5) == 2
        assert v7_to_v5[0].version == 8
        assert v7_to_v5[1].version == 7
        v6_to_v3 = self.gvc.get_diff_artifact_nodes(USER_NAME, PROJECT_NAME, node6_id, node3_id)
        assert len(v6_to_v3) == 2
        assert v6_to_v3[0].version == 7
        assert v6_to_v3[1].version == 6
        v6_to_v1 = self.gvc.get_diff_artifact_nodes(USER_NAME, PROJECT_NAME, node6_id, node1_id)
        assert len(v6_to_v1) == 3
        assert v6_to_v1[0].version == 7
        assert v6_to_v1[1].version == 6
        assert v6_to_v1[2].version == 3
    
    def test_two_chats(self):
        # add two chats
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, _, chat1_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        chat2 = chats.GoosvcChat(USER_NAME, CHAT2_NAME)
        branch_id, _, chat2_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id, chat2)
        # store two artifacts in two different chats
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file_1 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_1, MEDIA_TYPE_PNG)
        branch_id, node1_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat1_id, artifact1)
        input_file_2 = os.path.join(input_folder, FILE2_INPUT_NAME)
        artifact2 = StoreFileArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_FOLDER, input_file_2, MEDIA_TYPE_PNG)
        branch_id, node2_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat2_id, artifact2)
        # check if get_artifact_nodes works for both chats
        artifact_nodes1 = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, branch_id, chat1_id)
        self.assertEqual(len(artifact_nodes1), 1)
        self.assertEqual(artifact_nodes1[0].node_id, node1_id)
        artifact_nodes2 = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifact_nodes2), 1)
        self.assertEqual(artifact_nodes2[0].node_id, node2_id)
        # delete artifact in wrong chat
        artifact3 = DeleteArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER)
        self.gvc.delete_artifact(USER_NAME, PROJECT_NAME, branch_id, chat2_id, artifact3)
        # check if artifact was not deleted
        artifact_nodes1 = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, branch_id, chat1_id)
        self.assertEqual(len(artifact_nodes1), 1)
        artifact_nodes2 = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifact_nodes2), 1)
        # duplicate artifact1 in chat2
        branch_id, node4_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat2_id, artifact1)
        # check if artifact was duplicated in chat2
        artifact_nodes2 = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifact_nodes2), 2)
        # update artifact in chat2
        input_file_3 = os.path.join(input_folder, FILE3_INPUT_NAME)
        artifact3 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_3, MEDIA_TYPE_PNG)
        branch_id, node5_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat2_id, artifact3)
        # check if artifact was updated in chat2
        artifact_nodes2 = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifact_nodes2), 2)
        # check if the node was created correctly
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node5_id)
        self.assertTrue(type(node_read) is nodes.GoosvcNode)
        node_content = ArtifactNodeContent(**node_read.content)
        assert node_content.operation == "update"

    def test_scope(self):
        # add two chats
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, _, chat1_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        chat2 = chats.GoosvcChat(USER_NAME, CHAT2_NAME)
        branch_id, _, chat2_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id, chat2)
        # store one artifacts with scope "global" in chat1
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file_1 = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_1, MEDIA_TYPE_PNG, scope="global")
        branch_id, node1_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat1_id, artifact1)
        # check if artifact appears in both chats
        artifact_nodes1 = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, branch_id, chat1_id)
        self.assertEqual(len(artifact_nodes1), 1)
        self.assertEqual(artifact_nodes1[0].node_id, node1_id)
        artifact_nodes2 = self.gvc.get_artifact_nodes(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifact_nodes2), 1)
        self.assertEqual(artifact_nodes2[0].node_id, node1_id)
        artifacts_chat1 = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat1_id)
        self.assertEqual(len(artifacts_chat1), 1)
        artifacts_chat2 = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifacts_chat2), 1)
        # test add same artifact in chat2 is not allowed (for chat and global scope)
        self.assertRaises(GoosvcException, self.gvc.store_artifact, USER_NAME, PROJECT_NAME, branch_id, chat2_id, artifact1)
        artifact2 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file_1, MEDIA_TYPE_PNG, scope="global")
        self.assertRaises(GoosvcException, self.gvc.store_artifact, USER_NAME, PROJECT_NAME, branch_id, chat2_id, artifact2)
        # test delete global artifact in chat2 is not allowed
        artifact3 = DeleteArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER)
        branch_none_id, _ = self.gvc.delete_artifact(USER_NAME, PROJECT_NAME, branch_id, chat2_id, artifact3)
        self.assertIsNone(branch_none_id)
        artifacts_chat1 = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat1_id)
        self.assertEqual(len(artifacts_chat1), 1)
        artifacts_chat2 = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifacts_chat2), 1)
        # test rename global artifact in chat2 is not allowed
        artifact4 = RenameArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, "new_name.png", "new_path")
        branch_none_id, _ = self.gvc.rename_artifact(USER_NAME, PROJECT_NAME, branch_id, chat2_id, artifact4)
        self.assertIsNone(branch_none_id)
        # test rename global artifact in chat1 is allowed
        artifact5 = RenameArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, "new_name.png", "new_path")
        branch_id, node2_id = self.gvc.rename_artifact(USER_NAME, PROJECT_NAME, branch_id, chat1_id, artifact5)
        artifacts_chat1 = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat1_id)
        self.assertEqual(len(artifacts_chat1), 1)
        self.assertEqual(artifacts_chat1[0].filename, "new_name.png")
        artifacts_chat2 = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifacts_chat2), 1)
        self.assertEqual(artifacts_chat2[0].filename, "new_name.png")
        # check if the node was created correctly
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node2_id)
        # test delete global artifact in chat1 is allowed
        artifact6 = DeleteArtifact(USER_NAME, "new_name.png", "new_path")
        branch_id, node2_id = self.gvc.delete_artifact(USER_NAME, PROJECT_NAME, branch_id, chat1_id, artifact6)
        self.assertIsNotNone(branch_id)
        # check if the node was deleted correctly
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node2_id)
        self.assertTrue(type(node_read) is nodes.GoosvcNode)
        node_content = ArtifactNodeContent(**node_read.content)
        self.assertEqual(node_content.operation, "delete")
        # check if artifact was deleted in both chats
        artifacts_chat1 = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat1_id)
        self.assertEqual(len(artifacts_chat1), 0)
        artifacts_chat2 = self.gvc.get_artifacts(USER_NAME, PROJECT_NAME, branch_id, chat2_id)
        self.assertEqual(len(artifacts_chat2), 0)

    def test_media_type_guessing(self):
        # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, _, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # store artifact without media type
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file) # no media type given
        branch_id, node_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        # check if the node was created correctly
        node_read = self.gvc.get_node(USER_NAME, PROJECT_NAME, node_id)
        self.assertTrue(type(node_read) is nodes.GoosvcNode)
        node_content = ArtifactNodeContent(**node_read.content)
        self.assertEqual(node_content.media_type, MEDIA_TYPE_PNG)
        #  to be continued
        

