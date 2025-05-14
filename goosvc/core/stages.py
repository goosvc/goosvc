from dataclasses import dataclass
from goosvc.core.nodes import GoosvcNode, GoosvcNodes
from goosvc.core.exceptions import GoosvcException

@dataclass
class GoosvcStage:
    author: str
    stage_name: str
    stage_description: str

# Data class for storing stages content in nodes
@dataclass
class StageNodeContent:
    stage_name: str # must be unique within path
    stage_description: str

class GoosvcStages:
    def __init__(self, projects_dir: str,  nodes: GoosvcNodes):
        self.projects_dir = projects_dir
        self.nodes = nodes

    def add_stage(self, owner: str, project: str, id: str, stage: GoosvcStage):
        # TODO: check that stage does not exist
        exiting_stage_names = self.get_stage_names(owner, project, id)
        if stage.stage_name in exiting_stage_names:
            raise GoosvcException("1015")
        # create stage
        node_content = StageNodeContent(stage.stage_name, stage.stage_description)
        node = GoosvcNode("stage", id, stage.author, node_content)
        branch_id, node_id = self.nodes.add_node(owner, project, node)
        return branch_id, node_id
    
    def get_stage_node(self, owner: str, project: str, id: str, stage_name: str, root_id: str = None):
        stage_nodes = self.get_stage_nodes(owner, project, id)
        for stage_node in stage_nodes:
            node_content = StageNodeContent(**stage_node.content)
            if node_content.stage_name == stage_name:
                return stage_node
        return None
    
    def get_stage_nodes(self, owner: str, project: str, id: str, root_id: str = None):
        return self.nodes.get_path(owner, project, id, ["stage"], root_id)
    
    def get_stage_names(self, owner: str, project: str, id: str):
        stage_nodes = self.get_stage_nodes(owner, project, id)
        stage_names = []
        for stage_node in stage_nodes:
            node_content = StageNodeContent(**stage_node.content)
            stage_names.append(node_content.stage_name)
        return stage_names
    
    def stage_exists(self, owner: str, project: str, id: str, stage_name: str):
        return stage_name in self.get_stage_names(owner, project, id)