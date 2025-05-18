from typing import Union
from goosvc.core import  artifacts, chats, messages, nodes, projects, stages, branches, transactions
from goosvc.core import core as core
from goosvc.core.exceptions import GoosvcException

DEFAULT_BASE_DIR = "data"

class Goosvc:
    
    def __init__(self, base_dir: str = DEFAULT_BASE_DIR):
        self.core = core.GoosvcCore(base_dir)

    def permission(self, owner, project_name, user):
        return self.core.projects.get_access_permission(owner, project_name, user)
    
    # ----------------
    # Info functions
    # ----------------
    
    def get_branch_details(self, owner: str, project: str, branch_ids: list = None, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.info.get_branch_details(owner, project, branch_ids)
        raise GoosvcException("1002")
    
    # ----------------
    # Project functions
    # ----------------

    def get_project_names(self, owner, requester: str = "app"):
        if requester != "app" and requester != owner:
            return self.core.projects.get_public_project_names(owner)
        else:
            return self.core.projects.get_project_names(owner)

    def create_project(self, owner: str, project: str, project_description: str, requester: str = "app"):
        if requester != "app" and requester != owner:
            raise GoosvcException("1004")
        return self.core.projects.create_project(owner, project, project_description)
    
    def get_project(self, owner: str, project: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.projects.get_project(owner, project)
        raise GoosvcException("1002")

    def delete_project(self, owner: str, project: str, requester: str = "app"):
        if self.permission(owner, project, requester).admin:
            return self.core.projects.delete_project(owner, project)
        raise GoosvcException("1008")
    
    def set_access_permission(self, owner: str, project: str, user: str, new_permission: projects.GoosvcPermission, requester: str = "app"):
        if self.permission(owner, project, requester).admin:
            return self.core.projects.set_access_permission(owner, project, user, new_permission)
        raise GoosvcException("1008")
    
    def get_access_permission(self, owner: str, project: str, user: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.projects.get_access_permission(owner, project, user)
        return projects.GoosvcPermission(False, False, False)
    
    def set_private(self, owner: str, project: str, private: bool, requester: str = "app"):
        if self.permission(owner, project, requester).admin:
            return self.core.projects.set_private(owner, project, private)
        raise GoosvcException("1008")
    
    # ----------------
    # Admin functions
    # ----------------
    
    def lock_all_projects(self):
        return self.core.projects.lock_all_projects()
    
    # ----------------
    # Owner functions
    # ----------------
    
    def get_owners(self):
        return self.core.owners.get_owners()
    
    # ----------------
    # Branch functions
    # ----------------

    def get_branches(self, owner: str, project: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.branches.get_branches(owner, project)
        raise GoosvcException("1002")
    
    def get_branch_head(self, owner: str, project: str, branch_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.branches.get_branch_head(owner, project, branch_id)
        raise GoosvcException("1002")
    
    def get_heads(self, owner: str, project: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.branches.get_heads(owner, project)
        raise GoosvcException("1002")
    
    # Branch Groups

    def create_branch_group(self, owner: str, project: str, branch_group: branches.BranchGroup, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.branches.create_branch_group(owner, project, branch_group)
        raise GoosvcException("1009")
    
    def update_branch_group(self, owner: str, project: str, branch_group: branches.BranchGroup, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.branches.update_branch_group(owner, project, branch_group)
        raise GoosvcException("1009")
    
    def get_branch_group(self, owner: str, project: str, group_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.branches.get_branch_group(owner, project, group_id)
        raise GoosvcException("1002")
    
    def get_branch_groups(self, owner: str, project: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.branches.get_branch_groups(owner, project)
        raise GoosvcException("1002")
    
    # ----------------
    # Stage functions
    # ----------------

    def add_stage(self, owner: str, project: str, id: str, stage: stages.GoosvcStage, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.stages.add_stage(owner, project, id, stage)
        raise GoosvcException("1009")
    
    def get_stage_node(self, owner: str, project: str, id: str, stage_name: str, root_id: str = None, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.stages.get_stage_node(owner, project, id, stage_name, root_id)
        raise GoosvcException("1002")
    
    def get_stage_nodes(self, owner: str, project: str, id: str, root_id: str = None, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.stages.get_stage_nodes(owner, project, id, root_id)
        raise GoosvcException("1002")
    
    def get_stage_names(self, owner: str, project: str, id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.stages.get_stage_names(owner, project, id)
        raise GoosvcException("1002")
    
    # ----------------
    # Node functions
    # ----------------

    def add_node(self, owner: str, project: str, node: nodes.GoosvcNode, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.nodes.add_node(owner, project, node)
        raise GoosvcException("1009")

    def get_node(self, owner: str, project: str, node_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            node = self.core.nodes.get_node(owner, project, node_id)
            if node != None:
                return node
            raise GoosvcException("1025")
        raise GoosvcException("1002")
    
    def get_path(self, owner: str, project: str, id: str, type: list[str] = [], root_id: str = None, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.nodes.get_path(owner, project, id, type, root_id)
        raise GoosvcException("1002")
    
    def get_nodes(self, owner: str, project: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.nodes.get_nodes(owner, project)
        raise GoosvcException("1002")
    
    # ----------------
    # Artifact functions
    # ----------------

    def store_artifact(self, owner: str, project: str, id: str, chat_id: str, artifact: Union[artifacts.StoreFileArtifact, artifacts.StoreTextArtifact], requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.artifacts.store_artifact(owner, project, id, chat_id, artifact)
        raise GoosvcException("1009")
    
    def delete_artifact(self, owner: str, project: str, id: str, chat_id: str, artifact: artifacts.DeleteArtifact, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.artifacts.delete_artifact(owner, project, id, chat_id, artifact)
        raise GoosvcException("1009")
        
    def rename_artifact(self, owner: str, project: str, id: str, chat_id: str, artifact: artifacts.RenameArtifact, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.artifacts.rename_artifact(owner, project, id, chat_id, artifact)
        raise GoosvcException("1009")
    
    def get_artifact_file(self, owner: str, project: str, artifact_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.artifacts.get_artifact_file(owner, project, artifact_id)
        raise GoosvcException("1002")
    
    def get_artifact_name(self, owner: str, project: str, artifact_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.artifacts.get_artifact_name(owner, project, artifact_id)
        raise GoosvcException("1002")

    def get_artifact_nodes(self, owner: str, project: str, node_id: str, chat_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.artifacts.get_artifact_nodes(owner, project, node_id, chat_id)
        raise GoosvcException("1002")
    
    def get_artifact_node_by_name(self, owner: str, project: str, id: str, chat_id: str, filename: str, path: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.artifacts.get_artifact_node_by_name(owner, project, id, chat_id, filename, path)
        raise GoosvcException("1002")
        
    def get_artifacts(self, owner: str, project: str, id: str, chat_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.artifacts.get_artifacts(owner, project, id, chat_id)
        raise GoosvcException("1002")
    
    def get_diff_artifact_nodes(self, owner, project, from_node_id, to_node_id, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.artifacts.get_diff_artifact_nodes(owner, project, from_node_id, to_node_id)
        raise GoosvcException("1002")
    
    def get_all_artifact_versions(self, owner: str, project: str, id: str, artifact_node_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.artifacts.get_all_artifact_versions(owner, project, id, artifact_node_id)
        raise GoosvcException("1002")
    
    # ----------------
    # Merge functions
    # ----------------

    def merge(self, owner: str, project: str, author: str, head_ids: list[str], requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.merge.merge(owner, project, author, head_ids)
        raise GoosvcException("1009")
    
    # ----------------
    # Chat functions
    # ----------------

    def create_chat(self, owner: str, project: str, id: str, chat: chats.GoosvcChat, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.chats.create_chat(owner, project, id, chat)
        raise GoosvcException("1009")
    
    def get_chats(self, owner: str, project: str, id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.chats.get_chats(owner, project, id)
        raise GoosvcException("1002")
        
    def get_chat_node(self, owner: str, project: str, chat_id: str, id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.chats.get_chat_node(owner, project, chat_id, id)
        raise GoosvcException("1002")
        
    # ----------------
    # Message functions
    # ----------------
    
    def add_message(self, owner: str, project: str, id: str, message: messages.GoosvcMessage, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.messages.add_message(owner, project, id, message)
        raise GoosvcException("1009")
    
    def get_message_nodes(self, owner: str, project: str, chat_id: str, node_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.messages.get_message_nodes(owner, project, chat_id, node_id)
        raise GoosvcException("1002")
    
    def get_last_message_node(self, owner: str, project: str, chat_id: str, id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.messages.get_last_message_node(owner, project, chat_id, id)
        raise GoosvcException("1002")
    
    def get_messages(self, owner: str, project: str, chat_id: str, node_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.messages.get_messages(owner, project, chat_id, node_id)
        raise GoosvcException("1002")
    
    def get_message(self, owner: str, project: str, node_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.messages.get_message(owner, project, node_id)
        raise GoosvcException("1002")
    
    def get_message_node(self, owner: str, project: str, node_id: str, requester: str = "app"):
        if self.permission(owner, project, requester).read:
            return self.core.messages.get_message_node(owner, project, node_id)
        raise GoosvcException("1002")
    
    # ----------------
    # Transaction functions
    # ----------------

    def start_transaction(self, owner: str, project: str, id: str, transaction: transactions.GoosvcTransaction, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.transactions.start_transaction(owner, project, id, transaction)
        raise GoosvcException("1009")
    
    def end_transaction(self, owner: str, project: str, id: str, transaction: transactions.GoosvcTransaction, requester: str = "app"):
        if self.permission(owner, project, requester).write:
            return self.core.transactions.end_transaction(owner, project, id, transaction)
        raise GoosvcException("1009")
    

    



