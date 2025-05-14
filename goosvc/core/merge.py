import os
from dataclasses import dataclass
from goosvc.core.nodes import GoosvcNodes, GoosvcNode
from goosvc.core.artifacts import GoosvcArtifacts, ArtifactNodeContent
from goosvc.core.stages import GoosvcStages
from goosvc.core.chats import  ChatNodeContent, GoosvcChats
from goosvc.core.messages import GoosvcMessages
from goosvc.core.branches import GoosvcBranches
from goosvc.core import common as common
import dataclasses

# Data class for storing merge content in nodes
@dataclass
class MergeNodeContent:
    common_parent_id: str 
    head_ids: list[str]
    node_id_dict: dict[str, str]

class GoosvcMerge:
    def __init__(self, projects_dir: str, nodes: GoosvcNodes, artifacts: GoosvcArtifacts, stages: GoosvcStages, chats: GoosvcChats, messages:  GoosvcMessages, branches: GoosvcBranches):
        self.projects_dir = projects_dir
        self.nodes = nodes
        self.artifacts = artifacts
        self.stages = stages
        self.chats = chats
        self.messages = messages
        self.branches = branches

    def merge(self, owner: str, project: str, author: str, head_ids: list[str]):
        # replace branch ids with head ids
        merge_head_ids = []
        for head_id in head_ids:
            branch_head = self.branches.get_branch_head(owner, project, head_id)
            if branch_head == None:
                merge_head_ids.append(head_id)
            else:
                merge_head_ids.append(branch_head) 

        # get common parent
        common_parent_id = self.get_common_parent(owner, project, merge_head_ids)
        if common_parent_id == None:
            print("No common parent found")
            return None, None
        # print("Common parent:", common_parent_id)
        # check that merge branches contain no stages before common parent
        for head_id in merge_head_ids:
            stages = self.stages.get_stage_nodes(owner, project, head_id, common_parent_id)
            if len(stages) > 0:
                # print("Stage found in merge. No merge possible")
                # this cannot be resolved. no way out
                return None, None
        # check for merge conflicts
        merge_conflicts = self.get_merge_conflicts(owner, project, common_parent_id, merge_head_ids)
        if len(merge_conflicts) > 0:
            print("Merge conflicts found")
            # TODO: resolve merge conflicts (with defined branch order)
            return None, None
        
        # assemble nodes for merge (dry run)
        merge_nodes = []
        node_dict = {} # new node temp id -> old node
        all_chat_ids = set() # chat ids in all branches so far
        for head_id in merge_head_ids:
            path = self.nodes.get_path(owner, project, head_id, [], common_parent_id)
            if path == None:
                print(f"Node {head_id} not found")
                return None, None
            path = path[::-1] # reverse path
            current_branch_chat_dict = {}
            for node in path:
                if node.type == "message":
                    chat_id = node.content['chat_id']
                    if not chat_id in current_branch_chat_dict:
                        # new chat id in current branch. check if chat id already exists in merge
                        if chat_id in all_chat_ids:
                            # we have a problem: chat id is already used in another branch
                            # solution: branch chat from last message before common parent
                            # first: get chat node for chat_id to copy chat name and author
                            # print(f"Chat {chat_id} already exists in merge. Branching chat")
                            parent_chat_node = self.chats.get_chat_node(owner, project, chat_id, common_parent_id)
                            if parent_chat_node == None:
                                print(f"Chat {chat_id} not found")
                                return None, None
                            # second: get last message of the chat before the common parent
                            last_message_node = self.messages.get_last_message_node(owner, project, chat_id, common_parent_id)
                            if last_message_node == None:
                                # no messages before common parent: attach new chat to chat node
                                last_message_id = parent_chat_node.node_id
                            else:
                                last_message_id = last_message_node.node_id
                            # finally: create new chat node with last message id as parent chat node
                            new_chat_id = common.get_id()
                            new_chat_node_content = ChatNodeContent(parent_chat_node.content['chat_name']+".", new_chat_id, last_message_id)
                            new_chat_node = GoosvcNode("chat", None, parent_chat_node.author, dataclasses.asdict(new_chat_node_content)) # parent_id will be set on write
                            merge_nodes.append(new_chat_node)
                            new_chat_node.node_id = common.get_id()
                            # node_dict[new_chat_node.node_id] = None # chat node has no corresponding original node
                            # update chat id in current branch
                            current_branch_chat_dict[chat_id] = new_chat_id
                        else:
                            current_branch_chat_dict[chat_id] = chat_id
                    node.content['chat_id'] = current_branch_chat_dict[chat_id]
                new_node = GoosvcNode(node.type, None, node.author, node.content) # parent_id will be set on write
                # set temporary node id to find corresponding original node on write
                # this id will be replaced by the actual node id on write
                new_node.node_id = common.get_id()
                node_dict[new_node.node_id] = node
                merge_nodes.append(new_node)
            # update chat ids for next branch
            all_chat_ids.update(current_branch_chat_dict.keys())
        
        
        # write merge to repository
        last_node_id = common_parent_id
        merge_start_node_id = None
        message_id_map = {} # old message_id -> new message_id
        node_id_dict = {} # new node_id -> old node_id
        for node in merge_nodes:
            node.parent_id = last_node_id
            # update parent_chat_node_id for chat nodes if needed
            if node.type == "chat":
                if node.content['parent_chat_node_id'] != None:
                    if node.content['parent_chat_node_id'] in message_id_map: 
                        # parent chat node is before common parent: update required
                        node.content['parent_chat_node_id'] = message_id_map[node.content['parent_chat_node_id']]
            original_node_id = None
            if node.node_id in node_dict:
                original_node = node_dict[node.node_id] # use temporary node id to get original node
                original_node_id = original_node.node_id
            # add node
            _, last_node_id = self.nodes.add_node(owner, project, node, True) # node.node_id will be set by add_node. silent=True: no branch creation
            # set merge_start_node_id (used by end node)
            if merge_start_node_id == None:
                merge_start_node_id = last_node_id
            # update node_map (used by end node, documents merge process)
            # original_node_id is None for nodes not in the original branch
            node_id_dict[last_node_id] = original_node_id
            # update message_id_map (used by chat nodes to update parent_chat_node_id)
            if node.type == "message":
                old_message_id = original_node.node_id
                message_id_map[old_message_id] = last_node_id
        # append merge end node
        merge_node_content = MergeNodeContent(common_parent_id, merge_head_ids, node_id_dict)
        last_node = GoosvcNode("merge", last_node_id, author, merge_node_content) 
        branch_id, last_node_id = self.nodes.add_node(owner, project, last_node) # with this write the branch will be visible

        return branch_id, last_node_id
    
    # find earliest common ancestor for a list of nodes
    def get_common_parent(self, owner: str, project: str, head_ids: list[str]):
        num_nodes = len(head_ids)
        node_dict = {}
        for node_id in head_ids:
            path = self.nodes.get_path(owner, project, node_id)
            if path == None:
                print(f"Node {node_id} not found")
                return None
            for node in path:
                if node.node_id not in node_dict:
                    node_dict[node.node_id] = 0
                node_dict[node.node_id] += 1
                if node_dict[node.node_id] == num_nodes:
                    return node.node_id
        return None
    
    def get_merge_conflicts(self, owner: str, project: str, common_parent_id, head_ids: list[str]):
        # check for merge conflicts
        diff_artifacts_dict = {}
        merge_conflicts = {}
        for node_id in head_ids:
            diff_artifacts_nodes = self.artifacts.get_diff_artifact_nodes(owner, project, node_id, common_parent_id)
            for artifact_node in diff_artifacts_nodes:
                artifact = ArtifactNodeContent(**artifact_node.content)
                file = os.path.join(artifact.path, artifact.filename)
                if file not in diff_artifacts_dict:
                    diff_artifacts_dict[file] = [artifact_node.node_id]
                else:
                    # TODO: check if modifications are equal (no conflict)
                    diff_artifacts_dict[file].append(artifact_node.node_id)
                    merge_conflicts[file] = diff_artifacts_dict[file]
                    # print(f"Merge conflict: {file} in nodes {diff_artifacts_dict[file]}")
        return merge_conflicts

        