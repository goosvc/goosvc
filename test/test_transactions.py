import unittest
from goosvc.core import transactions, chats, messages
from goosvc.goosvc import Goosvc
from goosvc.core.exceptions import GoosvcException
import uuid
import os
from goosvc.core.artifacts import StoreFileArtifact, StoreTextArtifact

USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_stages"
TEST_TYPE1 = "test-type-1"

CHAT1_NAME = "Chat 1"
QUESTION1 = "Hello, this is a test message"
QUESTION2 = "Hello, this is another test message"
QUESTION3 = "Hello, this is a third test message"
RESPONSE1 = "Hello, this is a test response"
RESPONSE2 = "Hello, this is another test response"
RESPONSE3 = "Hello, this is a third test response"
ASSISTANT_NAME = "Assistant 1"

OUTPUT_FOLDER = "figures_top"
FILE1_INPUT_NAME = "figure1.png"
FILE2_INPUT_NAME = "figure2.png"
FILE1_OUTPUT_NAME = "figure_3.png"
FILE2_OUTPUT_NAME = "figure_4.png"
TEXT_FILE_NAME = "test_text.txt"
TEXT_FOLDER = "texts"
TEXT_CONTENT = "This is a test text content."

MEDIA_TYPE_TEXT = "text/plain"
MEDIA_TYPE_PNG = "image/png"
ORIGIN1 = "user input"

class TestTransactions(unittest.TestCase):

    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)

    def test_start_transaction(self):
        # create a transaction
        transaction = transactions.GoosvcTransaction(USER_NAME)
        branch_id, node_id, transaction_id = self.gvc.start_transaction(USER_NAME, PROJECT_NAME, None, transaction)
        self.assertIsNotNone(branch_id)
        self.assertIsNotNone(node_id)
        self.assertIsNotNone(transaction_id)
        # check if the transaction node is created correctly
        transaction_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, node_id)
        self.assertIsNotNone(transaction_node)
        self.assertEqual(transaction_node.type, "transaction_start")
        self.assertEqual(transaction_node.content["type"], "start")

    def test_start_before_ending_last_transaction(self):
        # create a transaction
        transaction = transactions.GoosvcTransaction(USER_NAME)
        branch_id, node_id, transaction_id = self.gvc.start_transaction(USER_NAME, PROJECT_NAME, None, transaction)
        self.assertIsNotNone(branch_id)
        self.assertIsNotNone(node_id)
        self.assertIsNotNone(transaction_id)
        # create a second transaction before ending the first one
        transaction2 = transactions.GoosvcTransaction(USER_NAME)
        with self.assertRaises(GoosvcException) as context:
            branch_id2, node_id2, transaction_id2 = self.gvc.start_transaction(USER_NAME, PROJECT_NAME, branch_id, transaction2)
        self.assertEqual(context.exception.code, "1026")
    
    def test_end_transaction(self):
        # create a transaction
        transaction_start = transactions.GoosvcTransaction(USER_NAME)
        branch_id, node_id, transaction_id = self.gvc.start_transaction(USER_NAME, PROJECT_NAME, None, transaction_start)
        self.assertIsNotNone(branch_id)
        self.assertIsNotNone(node_id)
        self.assertIsNotNone(transaction_id)
        # end the transaction
        transaction_end = transactions.GoosvcTransaction(USER_NAME, transaction_id)
        branch_id2, node_id2, transaction_id2 = self.gvc.end_transaction(USER_NAME, PROJECT_NAME, branch_id, transaction_end)
        self.assertIsNotNone(branch_id2)
        self.assertIsNotNone(node_id2)
        self.assertEqual(transaction_id2, transaction_id)
        # check if the transaction node is created correctly
        transaction_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, node_id2)
        self.assertIsNotNone(transaction_node)
        self.assertEqual(transaction_node.type, "transaction_end")
        self.assertEqual(transaction_node.content["type"], "end")
    
    def test_end_transaction_without_start(self):
        # end transaction without starting it (no transaction_id)
        transaction_end_1 = transactions.GoosvcTransaction(USER_NAME)
        with self.assertRaises(GoosvcException) as context:
            branch_id2, node_id2, transaction_id2 = self.gvc.end_transaction(USER_NAME, PROJECT_NAME, None, transaction_end_1)
        self.assertEqual(context.exception.code, "1030")
        # end transaction without starting it (invalid transaction_id)
        fake_id = uuid.uuid4().hex
        transaction_end_2 = transactions.GoosvcTransaction(USER_NAME, fake_id)
        with self.assertRaises(GoosvcException) as context:
            branch_id2, node_id2, transaction_id2 = self.gvc.end_transaction(USER_NAME, PROJECT_NAME, None, transaction_end_2)
        self.assertEqual(context.exception.code, "1027")

    def test_transaction_with_messages(self):
        # create chat 1
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, node1_id, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # create a transaction
        transaction = transactions.GoosvcTransaction(USER_NAME)
        branch_id, node_id, transaction_id = self.gvc.start_transaction(USER_NAME, PROJECT_NAME, branch_id, transaction)
        self.assertIsNotNone(transaction_id)
        # add message with invalid transaction id
        message1 = messages.GoosvcMessage(USER_NAME, QUESTION1, RESPONSE1, chat_id, ASSISTANT_NAME)
        with self.assertRaises(GoosvcException) as context:
            branch_id2, node_id2, message1_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message1)
        self.assertEqual(context.exception.code, "1026")
        # add messages with valid transaction id
        message2 = messages.GoosvcMessage(USER_NAME, QUESTION1, RESPONSE1, chat_id, ASSISTANT_NAME,None, None, transaction_id)
        branch_id, message1_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message2)
        message3 = messages.GoosvcMessage(USER_NAME, QUESTION2, RESPONSE2, chat_id, ASSISTANT_NAME,None, None, transaction_id)
        branch_id, message2_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message3)
        # check both messages have the same transaction id and version
        message1_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, message1_node_id)
        message2_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, message2_node_id)
        self.assertEqual(message1_node.transaction_id, message2_node.transaction_id)
        self.assertEqual(message1_node.version, message2_node.version)
        # end the transaction
        transaction_end = transactions.GoosvcTransaction(USER_NAME, transaction_id)
        branch_id2, node_id2, transaction_id2 = self.gvc.end_transaction(USER_NAME, PROJECT_NAME, branch_id, transaction_end)
        self.assertIsNotNone(node_id2)
        self.assertEqual(transaction_id2, transaction_id)
        # add message with transaction id after ending the transaction
        message4 = messages.GoosvcMessage(USER_NAME, QUESTION3, RESPONSE3, chat_id, ASSISTANT_NAME,None, None, transaction_id)
        with self.assertRaises(GoosvcException) as context:
            branch_id2, message3_node_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message4)
        self.assertEqual(context.exception.code, "1027")

    def test_transactions_with_artifacts(self):
         # add chat
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, chat_node_id, chat_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chat1)
        # create a transaction
        transaction = transactions.GoosvcTransaction(USER_NAME)
        branch_id, node_id, transaction_id = self.gvc.start_transaction(USER_NAME, PROJECT_NAME, branch_id, transaction)
        self.assertIsNotNone(transaction_id)
        # store artifact with invalid transaction id
        input_folder = os.path.join(os.path.dirname(__file__), "artifacts")
        input_file = os.path.join(input_folder, FILE1_INPUT_NAME)
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file, MEDIA_TYPE_PNG, None, ORIGIN1)
        with self.assertRaises(GoosvcException) as context:
            branch_id, node_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        self.assertEqual(context.exception.code, "1026")
        # store artifacts with valid transaction id
        artifact1 = StoreFileArtifact(USER_NAME, FILE1_OUTPUT_NAME, OUTPUT_FOLDER, input_file, MEDIA_TYPE_PNG, None, ORIGIN1, transaction_id)
        branch_id, node1_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact1)
        artifact2 = StoreFileArtifact(USER_NAME, FILE2_OUTPUT_NAME, OUTPUT_FOLDER, input_file, MEDIA_TYPE_PNG, None, ORIGIN1, transaction_id)
        branch_id, node2_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact2)
        artifact3 = StoreTextArtifact(USER_NAME, TEXT_FILE_NAME, TEXT_FOLDER, TEXT_CONTENT, MEDIA_TYPE_TEXT, None, ORIGIN1, transaction_id)
        branch_id, node3_id = self.gvc.store_artifact(USER_NAME, PROJECT_NAME, branch_id, chat_id, artifact3)
        # check all artifacts have the same transaction id and version
        artifact1_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, node1_id)
        artifact2_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, node2_id)
        artifact3_node = self.gvc.get_node(USER_NAME, PROJECT_NAME, node3_id)
        self.assertEqual(artifact1_node.transaction_id, artifact2_node.transaction_id, artifact3_node.transaction_id)
        self.assertEqual(artifact1_node.version, artifact2_node.version, artifact3_node.version)
        # end the transaction
        transaction_end = transactions.GoosvcTransaction(USER_NAME, transaction_id) 
        branch_id2, node_id2, transaction_id2 = self.gvc.end_transaction(USER_NAME, PROJECT_NAME, branch_id, transaction_end)
        self.assertIsNotNone(node_id2)
      