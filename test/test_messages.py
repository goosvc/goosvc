import unittest
import os
from goosvc.core import chats, messages
from goosvc.goosvc import Goosvc
from goosvc.core.artifacts import StoreFileArtifact, StoreTextArtifact
from goosvc.core.exceptions import GoosvcException


USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_chat"

CHAT1_NAME = "Chat 1"
ASSISTANT_NAME = "Assistant 1"
QUESTION1 = "Hello, this is a test message"
QUESTION2 = "Hello, this is another test message"
QUESTION3 = "Hello, this is a third test message"
RESPONSE1 = "Hello, this is a test response"
RESPONSE2 = "Hello, this is another test response"
RESPONSE3 = "Hello, this is a third test response"

TEXT_CONTENT = "This is a test text content."
TEXT_FOLDER = "texts"
IMAGE_FOLDER = "figures_top"

TEXT_FILE_NAME = "test_text.txt"
IMAGE_INPUT_NAME = "figure1.png"
IMAGE_OUTPUT_NAME = "figure_3.png"

MEDIA_TYPE_PNG = "image/png"
MEDIA_TYPE_TEXT = "text/plain"

class TestMessages(unittest.TestCase):
    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)

    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)

    def test_add_messages(self):
        # create chat 1
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, node1_id, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # add message with invalid chat id
        message1 = messages.GoosvcMessage(USER_NAME, QUESTION1, RESPONSE1, chat_id+"XYZ", ASSISTANT_NAME)
        self.assertRaises(GoosvcException, self.gvc.add_message, USER_NAME, PROJECT_NAME, branch_id, message1)
        # add message with valid chat id
        message1 = messages.GoosvcMessage(USER_NAME, QUESTION1, RESPONSE1, chat_id, ASSISTANT_NAME)
        branch_id, message1_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message1)
        self.assertIsNotNone(branch_id)
        self.assertIsNotNone(message1_node_id)
        # assert message1 is added to the chat
        message1_node = self.gvc.get_message(USER_NAME, PROJECT_NAME, message1_node_id)
        self.assertIsNotNone(message1_node)
        self.assertEqual(message1_node["request"], QUESTION1)
        self.assertEqual(message1_node["response"], RESPONSE1)
        self.assertEqual(message1_node["chat_id"], chat_id)


    def test_add_message_with_artifacts(self):
        # create chat 1
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, node1_id, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # add message with invalid request artifact id
        request_artifacts = {"first": "artifact1", "second": "artifact2"}
        message2 = messages.GoosvcMessage(USER_NAME, QUESTION2, RESPONSE2, chat_id, ASSISTANT_NAME, request_artifacts, None)
        self.assertRaises(GoosvcException, self.gvc.add_message, USER_NAME, PROJECT_NAME, branch_id, message2)
        # add two artifacts (text and image) to the chat
        artifact1 = StoreTextArtifact(USER_NAME, TEXT_FILE_NAME, TEXT_FOLDER, TEXT_CONTENT, MEDIA_TYPE_TEXT, None)
        branch_id, artifact1_node_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file = os.path.join(input_folder, IMAGE_INPUT_NAME)
        artifact2 = StoreFileArtifact(USER_NAME, IMAGE_OUTPUT_NAME, IMAGE_FOLDER, input_file, MEDIA_TYPE_PNG, None)
        branch_id, artifact2_node_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        # add message with valid request artifact id
        request_artifacts = {"first": artifact1_node_id, "second": artifact2_node_id}
        message2 = messages.GoosvcMessage(USER_NAME, QUESTION2, RESPONSE2, chat_id, ASSISTANT_NAME, request_artifacts, None)
        branch_id, message2_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message2)
        self.assertIsNotNone(branch_id)
        self.assertIsNotNone(message2_node_id)
        # assert message2 is added to the chat
        message2_node = self.gvc.get_message(USER_NAME, PROJECT_NAME, message2_node_id)
        self.assertIsNotNone(message2_node)
        self.assertEqual(message2_node["request"], QUESTION2)
        self.assertEqual(message2_node["response"], RESPONSE2)
        self.assertEqual(message2_node["chat_id"], chat_id)
        # assert artifacts are added to the message
        self.assertEqual(artifact1_node_id, message2_node["request_artifacts"]["first"])
        self.assertEqual(artifact2_node_id, message2_node["request_artifacts"]["second"])
        # add message with invalid response artifact id
        response_artifacts = {"first": "artifact3", "second": "artifact4"} 
        message3 = messages.GoosvcMessage(USER_NAME, QUESTION3, RESPONSE3, chat_id, ASSISTANT_NAME, None, response_artifacts)
        self.assertRaises(GoosvcException, self.gvc.add_message, USER_NAME, PROJECT_NAME, branch_id, message3)
        # add message with valid response artifact id
        response_artifacts = {"first": artifact1_node_id, "second": artifact2_node_id} 
        message3 = messages.GoosvcMessage(USER_NAME, QUESTION3, RESPONSE3, chat_id, ASSISTANT_NAME, None, response_artifacts)
        branch_id, message3_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message3)
        self.assertIsNotNone(branch_id)
        self.assertIsNotNone(message3_node_id)
        # assert artifacts are added to the message
        message3_node = self.gvc.get_message(USER_NAME, PROJECT_NAME, message3_node_id)
        self.assertEqual(artifact1_node_id, message3_node["response_artifacts"]["first"])
        self.assertEqual(artifact2_node_id, message3_node["response_artifacts"]["second"])



