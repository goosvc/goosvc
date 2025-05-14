from dataclasses import dataclass, field
from collections import defaultdict
from goosvc.core import nodes, chats
from goosvc.core.exceptions import GoosvcException

# Data class for adding a message 
@dataclass
class GoosvcMessage:
    author: str
    request: str
    response: str
    chat_id: str
    assistant: str = "unknown"
    request_artifacts: defaultdict[dict] = field(default_factory=lambda: defaultdict(dict)) # list of artifact node Ids in the request. value is the artifact node Id, key can be any string
    response_artifacts: defaultdict[dict] = field(default_factory=lambda: defaultdict(dict)) # list of artifact node Ids in the response. value is the artifact node Id, key can be any string  
    transaction_id: str = None # if the message is part of a transaction, else None

# Data class for storing chat message content in nodes
@dataclass
class MessageNodeContent:
    chat_id: str
    request: str
    response: str
    assistant: str
    request_artifacts: defaultdict[dict] = field(default_factory=lambda: defaultdict(dict)) # list of artifact node Ids in the request. value is the artifact node Id, key can be any string
    response_artifacts: defaultdict[dict] = field(default_factory=lambda: defaultdict(dict)) # list of artifact node Ids in the response. value is the artifact node Id, key can be any string

class GoosvcMessages:
    def __init__(self, projects_dir: str, nodes: nodes.GoosvcNodes, chats: chats.GoosvcChats):
        self.projects_dir = projects_dir
        self.nodes = nodes
        self.chats = chats

    # Returns a list of message nodes for a chat (identified by its chat_id) starting form id (node_id or branch_id)
    def get_message_nodes(self, owner: str, project: str, chat_id: str, id: str):
        if not self.chats.chat_exists(owner, project, id, chat_id):
            # Chat does not exist
            return []
        path = self.nodes.get_path(owner, project, id, ["message", "chat"])
        if path == None:
            return []
        messages = []
        next_node_id = None
        for node in path:
            # check if searching for parent chat
            if next_node_id != None:
                if node.node_id != next_node_id:
                    # Skip nodes that are not part of the chat
                    continue
                # parent chat found
                next_node_id = None
                chat_id = node.content["chat_id"] # chat continues with this chat_id
            # chat node with chat_id either marks the start of the chat or refers to a parent chat
            if node.type == "chat" and node.content["chat_id"] == chat_id:
                if node.content["parent_chat_node_id"] == None:
                    # chat starts here and there is no parent chat. Stop searching
                    break
                # chat continues from parent chat
                next_node_id = node.content["parent_chat_node_id"]
            if node.type == "message" and node.content["chat_id"] == chat_id:
                messages.append(node)
        messages.reverse()
        return messages
    
    def get_last_message_node(self, owner: str, project: str, chat_id: str, id: str):
        message_nodes = self.get_message_nodes(owner, project, chat_id, id)
        if len(message_nodes) == 0:
            return None
        return message_nodes[0]
    
    def get_message_node(self, owner: str, project: str, node_id: str):
        message_node = self.nodes.get_node(owner, project, node_id)
        if message_node == None:
            raise GoosvcException("1023")
        if message_node.type != "message":
            raise GoosvcException("1023")
        return message_node
    
    def get_message(self, owner: str, project: str, node_id: str):
        message_node = self.get_message_node(owner, project, node_id)
        if message_node == None:
            return None
        return message_node.content
    
    # Returns a list of messages for a chat starting form id (node_id or branch_id)
    def get_messages(self, owner: str, project: str, chat_id: str, id: str):
        message_nodes = self.get_message_nodes(owner, project, chat_id, id)
        if len(message_nodes) == 0:
            return []
        messages = []
        for message_node in message_nodes:
            messages.append(message_node.content)
        return messages

    def add_message(self, owner: str, project: str, id: str, message: GoosvcMessage):
        # check if referenced chat exists
        chat_id = message.chat_id
        if not self.chats.chat_exists(owner, project, id, chat_id):
            # Chat does not exist
            raise GoosvcException("1016")
        # check if referenced artifacts are valid
        if message.request_artifacts != None:
            for key, artifact_node_id in message.request_artifacts.items():
                if not self.nodes.is_node(owner, project, artifact_node_id,"artifact"):
                    raise GoosvcException("1024")
        else:
            message.request_artifacts = []
        if message.response_artifacts != None:
            for key, artifact_node_id in message.response_artifacts.items():
                if not self.nodes.is_node(owner, project, artifact_node_id,"artifact"):
                    raise GoosvcException("1024")
        else:
            message.response_artifacts = []
        node_content = MessageNodeContent(chat_id, message.request, message.response, message.assistant, message.request_artifacts, message.response_artifacts)
        node = nodes.GoosvcNode("message", id, message.author, node_content, None, None, None, message.transaction_id)
        branch_id, node_id = self.nodes.add_node(owner, project, node)
        return branch_id, node_id
