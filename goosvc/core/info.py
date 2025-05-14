import json
from dataclasses import dataclass
from goosvc.core.nodes import GoosvcNodes, GoosvcNode
from goosvc.core.artifacts import GoosvcArtifacts, ArtifactNodeContent
from goosvc.core.stages import GoosvcStages
from goosvc.core.chats import  ChatNodeContent, GoosvcChats
from goosvc.core.messages import GoosvcMessages
from goosvc.core.branches import GoosvcBranches
from goosvc.core import common as common
from goosvc.core.exceptions import GoosvcException
import dataclasses


@dataclass
class GoosvcInfoStage:
    stage_name: str
    stage_description: str
    node_id: str

@dataclass
class GoosvcInfoBranch:
    branch_id: str
    branch_head: str
    timestamp: str
    chats: list[ChatNodeContent] = dataclasses.field(default_factory=list)
    stages: list[GoosvcInfoStage] = dataclasses.field(default_factory=list)

class GoosvcInfo:
    def __init__(self, projects_dir: str, nodes: GoosvcNodes, artifacts: GoosvcArtifacts, stages: GoosvcStages, chats: GoosvcChats, messages:  GoosvcMessages, branches: GoosvcBranches):
        self.projects_dir = projects_dir
        self.nodes = nodes
        self.artifacts = artifacts
        self.stages = stages
        self.chats = chats
        self.messages = messages
        self.branches = branches

    # returns details of all branches for a given project if branch_ids is None
    # if branch_ids is not None, returns details of branches with the given ids
    def get_branch_details(self, owner: str, project: str, branch_ids: list = None):
        if branch_ids == None:
            branch_ids = self.branches.get_branches(owner, project)
        branch_details = []
        for branch_id in branch_ids:
            head_node = self.nodes.get_node(owner, project, branch_id)
            if head_node == None:
                raise GoosvcException("1012")
            stages = self.stages.get_stage_nodes(owner, project, branch_id)
            chats = self.chats.get_chats(owner, project, branch_id)
            branch_info = GoosvcInfoBranch(branch_id, head_node.node_id, head_node.timestamp, chats, [])
            for stage in stages:
                node_content = GoosvcInfoStage(stage.content["stage_name"], stage.content["stage_description"], stage.node_id)
                branch_info.stages.append(node_content)
            branch_details.append(dataclasses.asdict(branch_info))
        # sort array by timestamp
        branch_details.sort(key=lambda x: x["timestamp"])
        return branch_details
    
