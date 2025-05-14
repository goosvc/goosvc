import unittest
from goosvc.core import chats, messages
from goosvc.goosvc import Goosvc


USER_NAME = "test_user"
PROJECT_NAME = "unittest_test_chat"

CHAT1_NAME = "Chat 1"
CHAT2_NAME = "Chat 2"
CHAT3_NAME = "Chat 3"
ASSISTANT_NAME = "Assistant 1"
QUESTION1 = "Hello, this is a test message"
QUESTION2 = "Hello, this is another test message"
QUESTION3 = "Hello, this is a third test message"
QUESTION4 = "Hello, this is a fourth test message"
RESPONSE1 = "Hello, this is a test response"
RESPONSE2 = "Hello, this is another test response"
RESPONSE3 = "Hello, this is a third test response"
RESPONSE4 = "Hello, this is a fourth test response"

class TestChats(unittest.TestCase):
    def setUp(self):
        self.gvc = Goosvc("data-test")
        self.gvc.create_project(USER_NAME, PROJECT_NAME)
    
    def tearDown(self):
        self.gvc.delete_project(USER_NAME, PROJECT_NAME)

    def test_create_chat(self):
        branch_id, chat1_id, _ = self.create_one_chat(None)
        self.assertIsNotNone(chat1_id)
        # check if the chat was created correctly
        chat_read = self.gvc.get_chats(USER_NAME, PROJECT_NAME, branch_id)
        assert len(chat_read) == 1
        assert chat_read[0]['chat_name'] == CHAT1_NAME
        assert chat_read[0]['chat_id'] == chat1_id
        assert chat_read[0]['parent_chat_node_id'] == None

    def test_create_two_chats(self):
        branch_id, chat1_id, chat2_id = self.create_two_chats(None)
        self.assertIsNotNone(chat1_id)
        self.assertIsNotNone(chat2_id)
        # check if the chat was created correctly
        chat_read = self.gvc.get_chats(USER_NAME, PROJECT_NAME, branch_id)
        assert len(chat_read) == 2
        assert chat_read[1]['chat_name'] == CHAT1_NAME
        assert chat_read[1]['chat_id'] == chat1_id
        assert chat_read[1]['parent_chat_node_id'] == None
        assert chat_read[0]['chat_name'] == CHAT2_NAME
        assert chat_read[0]['chat_id'] == chat2_id
        assert chat_read[0]['parent_chat_node_id'] == None
    
    def test_one_chat_with_messages(self):
        branch1_id, chat1_id, chat_node_id = self.create_one_chat(None)
        # add two message to the chat
        question1 = messages.GoosvcMessage(USER_NAME, QUESTION1, RESPONSE1, chat1_id, ASSISTANT_NAME)
        branch1_id, node1_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch1_id, question1)
        response1 = messages.GoosvcMessage(USER_NAME, QUESTION2, RESPONSE2, chat1_id)
        branch2_id, node2_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, node1_id, response1)
        assert branch2_id == branch1_id
        assert node1_id != None
        assert node2_id != None
        # check if the messages was added correctly
        messages1_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat1_id, node1_id)
        assert len(messages1_nodes) == 1
        messages2_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat1_id, node2_id)
        assert len(messages2_nodes) == 2
        assert messages2_nodes[0].parent_id == chat_node_id
        assert messages2_nodes[0].author == USER_NAME
        assert messages2_nodes[0].content['chat_id'] == chat1_id
        assert messages2_nodes[0].content['request'] == QUESTION1
        assert messages2_nodes[0].content['response'] == RESPONSE1
        assert messages2_nodes[0].content['assistant'] == ASSISTANT_NAME
        assert messages2_nodes[1].parent_id == node1_id
        assert messages2_nodes[1].author == USER_NAME
        assert messages2_nodes[1].content['chat_id'] == chat1_id
        assert messages2_nodes[1].content['request'] == QUESTION2
        assert messages2_nodes[1].content['response'] == RESPONSE2
        assert messages2_nodes[1].content['assistant'] == 'unknown'
        # test get_messages
        messages1_nodes = self.gvc.get_messages(USER_NAME, PROJECT_NAME, chat1_id, node1_id)
        assert len(messages1_nodes) == 1
        assert messages1_nodes[0]['request'] == QUESTION1
        assert messages1_nodes[0]['response'] == RESPONSE1
        messages2_nodes = self.gvc.get_messages(USER_NAME, PROJECT_NAME, chat1_id, node2_id)
        assert len(messages2_nodes) == 2
        assert messages1_nodes[0]['request'] == QUESTION1
        assert messages1_nodes[0]['response'] == RESPONSE1
        assert messages2_nodes[1]['request'] == QUESTION2
        assert messages2_nodes[1]['response'] == RESPONSE2

    def test_two_chats_with_messages(self):
        branch_id, chat1_id, chat2_id = self.create_two_chats(None)
        # add two message to the first chat
        question1 = messages.GoosvcMessage(USER_NAME, QUESTION1, RESPONSE1, chat1_id)
        branch_id, node1_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, question1)
        response1 = messages.GoosvcMessage(USER_NAME, QUESTION2, RESPONSE2, chat1_id)
        branch_id, node2_id = self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, response1)
        self.gvc.core.nodes.get_node(USER_NAME, PROJECT_NAME, branch_id).node_id
        # add two message to the second chat
        question2 = messages.GoosvcMessage(USER_NAME, QUESTION3, RESPONSE3, chat2_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, question2)
        response2 = messages.GoosvcMessage(USER_NAME, QUESTION4, RESPONSE4, chat2_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, response2)
        # check if the messages was added correctly
        messages1_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat1_id, branch_id)
        assert len(messages1_nodes) == 2
        assert messages1_nodes[0].content['chat_id'] == chat1_id
        assert messages1_nodes[0].content['request'] == QUESTION1
        assert messages1_nodes[0].content['response'] == RESPONSE1
        assert messages1_nodes[1].content['chat_id'] == chat1_id
        assert messages1_nodes[1].content['request'] == QUESTION2
        assert messages1_nodes[1].content['response'] == RESPONSE2
        messages2_nodes = self.gvc.get_message_nodes(USER_NAME, PROJECT_NAME, chat2_id, branch_id)
        assert len(messages2_nodes) == 2
        assert messages2_nodes[0].content['chat_id'] == chat2_id
        assert messages2_nodes[0].content['request'] == QUESTION3
        assert messages2_nodes[0].content['response'] == RESPONSE3
        assert messages2_nodes[1].content['chat_id'] == chat2_id
        assert messages2_nodes[1].content['request'] == QUESTION4
        assert messages2_nodes[1].content['response'] == RESPONSE4
    
    # A1-A2-A3-B1-B2-C1-C2-A4-B3-C3 (single branch)
    #     |__________| 
    # chat A: A1-A2-A3-A4
    # chat B: B1-B2-B3
    # chat C: A1-A2-C1-C2-C3
    def test_parent_chat(self):
        # create chat A
        chatA = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, _, chatA_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, None, chatA)
        # write messages A1-A2-A3
        message = messages.GoosvcMessage(USER_NAME, "Request A1", "...", chatA_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        message = messages.GoosvcMessage(USER_NAME, "Request A2", "...", chatA_id)
        _, nodeA2_id =self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        message = messages.GoosvcMessage(USER_NAME, "Request A3", "...", chatA_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        # create chat B (no parent chat)
        chatB = chats.GoosvcChat(USER_NAME, CHAT2_NAME)
        branch_id, _, chatB_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id, chatB)
        # write messages B1-B2
        message = messages.GoosvcMessage(USER_NAME, "Request B1", "...", chatB_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        message = messages.GoosvcMessage(USER_NAME, "Request B2", "...", chatB_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        # create chat C (parent chat node A2)
        chatC = chats.GoosvcChat(USER_NAME, CHAT3_NAME,nodeA2_id)
        branch_id, _, chatC_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id, chatC)
        # write messages C1-C2
        message = messages.GoosvcMessage(USER_NAME, "Request C1", "...", chatC_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        message = messages.GoosvcMessage(USER_NAME, "Request C2", "...", chatC_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        # write messages A4-B3-C3
        message = messages.GoosvcMessage(USER_NAME, "Request A4", "...", chatA_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        message = messages.GoosvcMessage(USER_NAME, "Request B3", "...", chatB_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        message = messages.GoosvcMessage(USER_NAME, "Request C3", "...", chatC_id)
        self.gvc.add_message(USER_NAME, PROJECT_NAME, branch_id, message)
        # check number of chats
        current_chats = self.gvc.get_chats(USER_NAME, PROJECT_NAME, branch_id)
        self.assertEqual(len(current_chats), 3)
        # check number of branches
        branches = self.gvc.core.branches.get_branches(USER_NAME, PROJECT_NAME)
        self.assertEqual(len(branches), 1)
        # check chat A messages
        messagesA = self.gvc.get_messages(USER_NAME, PROJECT_NAME, chatA_id, branch_id)
        self.assertEqual(len(messagesA), 4)
        self.assertEqual(messagesA[0]['request'], "Request A1")
        self.assertEqual(messagesA[1]['request'], "Request A2")
        self.assertEqual(messagesA[2]['request'], "Request A3")
        self.assertEqual(messagesA[3]['request'], "Request A4")
        # check chat B messages
        messagesB = self.gvc.get_messages(USER_NAME, PROJECT_NAME, chatB_id, branch_id)
        self.assertEqual(len(messagesB), 3)
        self.assertEqual(messagesB[0]['request'], "Request B1")
        self.assertEqual(messagesB[1]['request'], "Request B2")
        self.assertEqual(messagesB[2]['request'], "Request B3")
        # check chat C messages
        messagesC = self.gvc.get_messages(USER_NAME, PROJECT_NAME, chatC_id, branch_id)
        self.assertEqual(len(messagesC), 5)
        self.assertEqual(messagesC[0]['request'], "Request A1")
        self.assertEqual(messagesC[1]['request'], "Request A2")
        self.assertEqual(messagesC[2]['request'], "Request C1")
        self.assertEqual(messagesC[3]['request'], "Request C2")
        self.assertEqual(messagesC[4]['request'], "Request C3")
    
    # helper functions
    def create_one_chat(self, parent_id):
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, node1_id, chat1_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, parent_id, chat1)
        return branch_id, chat1_id, node1_id
    
    def create_two_chats(self, parent_id):
        chat1 = chats.GoosvcChat(USER_NAME, CHAT1_NAME)
        branch_id, node1_id, chat1_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, parent_id, chat1)
        chat2 = chats.GoosvcChat(USER_NAME, CHAT2_NAME)
        branch_id, node2_id, chat2_id = self.gvc.create_chat(USER_NAME, PROJECT_NAME, branch_id, chat2)
        return branch_id, chat1_id, chat2_id

        