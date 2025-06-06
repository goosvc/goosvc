import os
import json
from dataclasses import dataclass
import dataclasses
from goosvc.core import common as common
from goosvc.core import nodes
from goosvc.core.exceptions import GoosvcException


@dataclass
class GoosvcChat:
    author: str
    chat_name: str # name helping to identify the chat. It is not unique
    parent_chat_node_id: str = None # chat continues from this message node. If None, chat is new
    chat_id: str = None  # ID of the chat generated by the system

@dataclass
class ChatNodeContent:
    chat_name: str
    chat_id: str
    parent_chat_node_id: str = None # chat continues from this node. If None, chat is new


class GoosvcChats:
    def __init__(self, projects_dir: str, nodes: nodes.GoosvcNodes):
        self.projects_dir = projects_dir
        self.nodes = nodes

    def create_chat(self, owner: str, project: str, id: str, chat: GoosvcChat):
        chat_id = common.get_id()
        chat.chat_id = chat_id
        if chat.parent_chat_node_id != None:
            # Check if parent chat node exists
            parent_chat_node = self.nodes.get_node(owner, project, chat.parent_chat_node_id)
            if parent_chat_node == None:
                # Parent chat node does not exist
                raise GoosvcException("1013")
            if parent_chat_node.type != "message":
                # Parent chat node is not a chat
                raise GoosvcException("1014")
        chat_node_content = ChatNodeContent(chat.chat_name, chat_id, chat.parent_chat_node_id)
        chat_node = nodes.GoosvcNode("chat", id, chat.author, chat_node_content)
        branch_id, node_id = self.nodes.add_node(owner, project, chat_node)
        return branch_id, node_id, chat_id
    
    # returns all chats for a given node_id or branch_id    
    def get_chats(self, owner: str, project: str, id: str):
        path = self.nodes.get_path(owner, project, id, ["chat"])
        chats = []
        for node in path:
            chats.append(node.content)
        return chats
    
    def get_chat_node(self, owner: str, project: str, chat_id: str, id: str):
        path = self.nodes.get_path(owner, project, id, ["chat"])
        if path == None:
            return []
        for node in path:
            if node.content["chat_id"] == chat_id:
                return node
        return None
    
    def chat_exists(self, owner: str, project: str, id: str, chat_id: str):
        chats = self.get_chats(owner, project, id)
        for chat in chats:
            if chat["chat_id"] == chat_id:
                return True
        return False
    
 