import os
import re
import pathlib
from dataclasses import dataclass
from typing import Union
from goosvc.core import common as common
from goosvc.core.nodes import GoosvcNodes, GoosvcNode
from goosvc.core.chats import GoosvcChats
from goosvc.core.exceptions import GoosvcException
import mimetypes

MAX_FILE_SIZE_MB = 10

# Data classes for storing new artifacts
@dataclass
class StoreFileArtifact:
    author: str
    filename: str
    path: str
    input_file: str = None
    media_type: str = None
    scope: str = 'chat' # chat or global
    origin: str = None # origin of the file (e.g. url, local file, etc.)
    transaction_id: str = None # if the message is part of a transaction, else None


@dataclass
class StoreTextArtifact:
    author: str
    filename: str
    path: str
    file_content: str = None
    media_type: str = None
    scope: str = 'chat' # chat or global
    origin: str = None # origin of the file (e.g. url, local file, etc.)
    transaction_id: str = None # if the message is part of a transaction, else None


@dataclass
class DeleteArtifact:
    author: str
    filename: str
    path: str

@dataclass
class RenameArtifact:
    author: str
    filename_old: str
    path_old: str
    filename_new: str
    path_new: str

# Data class for storing artifact content in nodes
@dataclass
class ArtifactNodeContent:
    artifact_id: str # ID of the artifact, used as filename
    chat_id: str     # ID of the chat
    operation: str   # add, update, delete
    filename: str    # filename for checkout
    path: str        # path for checkout
    filehash: str    # hash of the file
    media_type: str = None # media type of the file (none for delete operation)
    scope: str = 'chat' # chat or global
    origin: str = None # origin of the file (e.g. url, local file, etc.)

class GoosvcArtifacts:
    def __init__(self, projects_dir: str, nodes: GoosvcNodes, chats: GoosvcChats):
        self.projects_dir = projects_dir
        self.nodes = nodes
        self.chats = chats
    
    def store_artifact(self, owner: str, project: str, id: str, chat_id: str, artifact: Union[StoreFileArtifact, StoreTextArtifact]):
        if not self.chats.chat_exists(owner, project, id, chat_id):
            raise GoosvcException("1016")
        # check if path is valid
        if len(re.findall("[^a-zA-Z0-9_\-\\/]", artifact.path)) > 0:
            raise GoosvcException("1021")
        #  check if filename is valid
        filename_stem = pathlib.Path(artifact.filename).stem
        filename_path = pathlib.Path(artifact.filename).parent
        if len(re.findall("[^a-zA-Z0-9_\-]", filename_stem)) > 0 or str(filename_path) != '.': 
            raise GoosvcException("1022")
        operation = self.__get_operation(owner, project, id, chat_id, artifact)
        if operation == "invalid":
            raise GoosvcException("1017")
        # save artifact to artifact pool
        artifact_id = common.get_id()
        if isinstance(artifact, StoreTextArtifact):
            # store text artifact
            artifact_file = common.get_artifact_file(self.projects_dir, owner, project, artifact_id)
            with open(artifact_file, 'w') as dst:
                dst.write(artifact.file_content)
        elif isinstance(artifact, StoreFileArtifact):
            # store file artifact
            # check input file
            input_file = artifact.input_file
            if input_file == None or input_file == "":
                raise GoosvcException("1018")
            if not os.path.exists(input_file):
                raise GoosvcException("1018")
            if os.path.isdir(input_file):
                raise GoosvcException("1018")
            # check file size
            file_size = os.path.getsize(input_file)
            if file_size == 0:
                raise GoosvcException("1019")
            file_size_mb = file_size / (1024 * 1024)
            if file_size_mb >  MAX_FILE_SIZE_MB:
                raise GoosvcException("1020")
            # save file to artifact pool
            artifact_file = common.get_artifact_file(self.projects_dir, owner, project, artifact_id)
            with open(input_file, 'rb') as src, open(artifact_file, 'wb') as dst:
                dst.write(src.read())
        else:
            raise GoosvcException("1018")
        # add artifact node to version tree
        filehash = common.get_file_hash(artifact_file)
        if artifact.media_type == None:
            artifact.media_type = mimetypes.guess_type(artifact.filename)[0]
        node_content = ArtifactNodeContent(artifact_id, chat_id, operation, artifact.filename, artifact.path, filehash, artifact.media_type, artifact.scope, artifact.origin)
        node = GoosvcNode("artifact", id, artifact.author, node_content, None, None, None, artifact.transaction_id)
        branch_id, node_id = self.nodes.add_node(owner, project, node)
        return branch_id, node_id
    
    def delete_artifact(self, owner: str, project: str, id: str, chat_id: str, artifact: DeleteArtifact):
        if not self.chats.chat_exists(owner, project, id, chat_id):
            return None, "Chat not found"
        artifact_path = self.get_artifact_nodes(owner, project, id, chat_id)
        for node in artifact_path:
            if node.content['filename'] == artifact.filename and node.content['path'] == artifact.path:
                if node.content['operation'] != "delete":
                    # file exists and is not marked for deletion
                    scope = node.content['scope']
                    if scope == "global":
                        #  check chat_id
                        if node.content['chat_id'] != chat_id:
                            # file is not part of the chat. global artifacts can only be deleted in the cheat they are created in
                            return None, "Artifact not part of chat"
                    # delete artifact file
                    node_content = ArtifactNodeContent(None, chat_id, "delete", artifact.filename, artifact.path, None, None, scope)
                    node = GoosvcNode("artifact", id, artifact.author, node_content)
                    branch_id, node_id = self.nodes.add_node(owner, project, node)
                    return branch_id, node_id
                return None, "Artifact already deleted"
        return None, "Artifact not found"
    
    def rename_artifact(self, owner: str, project: str, id: str, chat_id: str, artifact: RenameArtifact):
        if not self.chats.chat_exists(owner, project, id, chat_id):
            return None, "Chat not found"
        artifacts = self.get_artifacts(owner, project, id, chat_id)
        if artifacts == None:
            return None, "Artifact not found"
        for node in artifacts:
            if node.filename == artifact.filename_old and node.path == artifact.path_old:
                scope = node.scope
                if scope == "global" and node.chat_id != chat_id:
                    # artifact is global and not part of the chat. 
                    # global artifacts can only modified in the chat they were created in
                    return None, "Artifact not part of chat"
                # rename artifact: 
                # delete old artifact 
                del_node_content = ArtifactNodeContent(None, chat_id, "delete", artifact.filename_old, artifact.path_old, None, None, node.scope)
                del_node = GoosvcNode("artifact", id, artifact.author, del_node_content)
                self.nodes.add_node(owner, project, del_node)
                # add new artifact
                add_node_content = ArtifactNodeContent(node.artifact_id, chat_id, "add", artifact.filename_new, artifact.path_new, node.filehash, node.media_type, node.scope)
                add_node = GoosvcNode("artifact", id, artifact.author, add_node_content)
                branch_id, node_id = self.nodes.add_node(owner, project, add_node)
                return branch_id, node_id
        return None, "Artifact not found"
    
    # Returns a list of all artifact nodes for a chat (identified by its chat_id) starting form id (node_id or branch_id)
    def get_all_artifact_nodes(self, owner: str, project: str, id: str, chat_id: str):
         # check if chat exists
        if not self.chats.chat_exists(owner, project, id, chat_id):
            # Chat does not exist
            return []
        path = self.nodes.get_path(owner, project, id, ["artifact", "chat"])
        if path == None:
            return []
        artifacts = []
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
            # its an artifact node: check if artifact node is part of the chat or is global
            if node.type == "artifact":
                if node.content["chat_id"] == chat_id or node.content["scope"] == "global":
                    artifacts.append(node)
        return artifacts
    
    # Returns a list of all VISIBLE artifact nodes for a chat (identified by its chat_id) starting form id (node_id or branch_id)
    def get_artifact_nodes(self, owner: str, project: str, id: str, chat_id: str):
        all_artifact_nodes = self.get_all_artifact_nodes(owner, project, id, chat_id)
        if all_artifact_nodes == None:
            return []
        return self.__get_diff_from_path(all_artifact_nodes)
    
    # returns the artifact node for a given artifact (identified by filename and path) in a chat (identified by its chat_id)
    def get_artifact_node_by_name(self, owner: str, project: str, id: str, chat_id: str, filename: str, path: str):
        artifact_nodes = self.get_artifact_nodes(owner, project, id, chat_id)
        for artifact_node in artifact_nodes:
            if artifact_node.content['filename'] == filename and artifact_node.content['path'] == path:
                return artifact_node
        return None
    
    # returns the artifact node for a given artifact (identified by path) in a chat (identified by its chat_id)
    def get_artifact_nodes_by_path(self, owner: str, project: str, id: str, chat_id: str, path: str, exclude_filenames:list):
        artifact_nodes = self.get_artifact_nodes(owner, project, id, chat_id)
        artifact_nodes = [artifact_node for artifact_node in artifact_nodes if artifact_node.content['path'] == path and artifact_node.content['filename'] not in exclude_filenames]
        
        return artifact_nodes
    
    # returns the artifact node for a given artifact (identified by its artifact_id)
    def get_artifact_node(self, owner: str, project: str, artifact_id: str):
        artifact_node = self.nodes.get_node(owner, project, artifact_id)
        if artifact_node == None:
            raise GoosvcException("1024")
        if artifact_node.type != "artifact":
            raise GoosvcException("1024")
        return artifact_node
    
    # returns all artifacts for a given node_id or branch_id visible in the indicated chat
    def get_artifacts(self, owner: str, project: str, id: str, chat_id: str):
        artifact_nodes = self.get_artifact_nodes(owner, project, id, chat_id)
        artifacts = []
        for artifact_node in artifact_nodes:
            if artifact_node.content['operation'] != "delete":
                artifacts.append(ArtifactNodeContent(**artifact_node.content))
        return artifacts
    
    # return all versions of an artifact (identified by filename and path) 
    def get_all_artifact_versions(self, owner: str, project: str, id: str, artifact_node_id: str):
        artifact_node = self.nodes.get_node(owner, project, artifact_node_id)
        if artifact_node == None:
            return []
        if artifact_node.type != "artifact":
            return []
        filename = artifact_node.content['filename']
        path = artifact_node.content['path']
        chat_id = artifact_node.content['chat_id']
        artifact_nodes = self.get_all_artifact_nodes(owner, project, id, chat_id)
        artifacts = []
        for artifact_node in artifact_nodes:
            if artifact_node.content['operation'] != "delete":
                if artifact_node.content['filename'] == filename and artifact_node.content['path'] == path:
                    artifacts.append(artifact_node)
        # reverse order to get the latest version last
        artifacts.reverse()
        return artifacts
    
    def get_artifact_file(self, owner: str, project: str, artifact_id: str):
        return common.get_artifact_file(self.projects_dir, owner, project, artifact_id)
    
    def get_artifact_name(self, owner: str, project: str, artifact_id: str):
        artifact_node = self.nodes.get_node(owner, project, artifact_id)
        if artifact_node == None:
            return None
        if artifact_node.type != "artifact":
            return None
        filename = artifact_node.content['filename']
        path = artifact_node.content['path']
        name_and_path = os.path.join(path, filename)
        #  replace \ with /
        name_and_path = re.sub(r'\\', '/', name_and_path)
        return name_and_path
    
    # returns all artifacts nodes changed between from_node and to_node
    def get_diff_artifact_nodes(self, owner, project, from_node_id, to_node_id):
        from_node = self.nodes.get_node(owner, project, from_node_id)
        to_node = self.nodes.get_node(owner, project, to_node_id)
        if from_node == None or to_node == None:
            return []
        if from_node.version < to_node.version:
            node2 = from_node
            node1 = to_node # older node
        else:
            node2 = to_node
            node1 = from_node # older node
        path = self.nodes.get_path(owner,project,node1.node_id,["artifact"],node2.node_id)
        if path == None:
            return []
        return self.__get_diff_from_path(path)
    
    def __get_diff_from_path(self, path):
        if path == None:
            return []
        artifacts_dict ={}
        for node in path:
            pathname = node.content['path']
            filename = node.content['filename']
            name = os.path.join(pathname, filename)
            if not name in artifacts_dict:
                artifacts_dict[name] = node
        artifacts = []  
        for artifact in artifacts_dict.values():
            # if artifact.content['operation'] != "delete":
            artifacts.append(artifact)
        return artifacts
    
    def __get_operation(self, owner: str, project: str, id: str, chat_id: str, artifact: Union[StoreFileArtifact, StoreTextArtifact]):
        artifact_path = self.get_artifact_nodes(owner, project, id, chat_id)
        if artifact_path == None:
            return "add"
        # check if artifact already exists
        for node in artifact_path:
            if node.content['filename'] == artifact.filename and node.content['path'] == artifact.path:
                scope = node.content['scope']
                if scope == "global" and node.content['chat_id'] != chat_id:
                    # artifact is global and not part of the chat. 
                    # global artifacts can only modified in the chat they were created in
                    return "invalid"
                if node.content['operation'] == "delete":
                    return "add"
                return "update"
        return "add"