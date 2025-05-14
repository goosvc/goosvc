import os
from dataclasses import dataclass
from goosvc.core import artifacts, branches, chats, messages, merge, nodes, owners, projects, stages, info, transactions


DEFAULT_BASE_DIR = "data"

@dataclass
class GoosvcUser:
    name: str
    email: str

class GoosvcCore:
    
    def __init__(self, base_dir: str = DEFAULT_BASE_DIR):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        self.projects_dir = os.path.join(base_dir, "projects")
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)
        # old school dependency injection
        self.owners = owners.GoosvcOwners(self.projects_dir)
        self.projects = projects.GoosvcProjects(self.projects_dir, self.owners)
        self.branches = branches.GoosvcBranches(self.projects_dir, self.projects)
        self.nodes = nodes.GoosvcNodes(self.projects_dir,self.branches, self.projects)
        self.chats = chats.GoosvcChats(self.projects_dir, self.nodes)
        self.transactions = transactions.GoosvcTransactions(self.projects_dir, self.nodes)
        self.messages = messages.GoosvcMessages(self.projects_dir, self.nodes, self.chats)
        self.artifacts = artifacts.GoosvcArtifacts(self.projects_dir, self.nodes, self.chats)
        self.stages = stages.GoosvcStages(self.projects_dir, self.nodes)
        self.merge = merge.GoosvcMerge(self.projects_dir, self.nodes, self.artifacts, self.stages, self.chats, self.messages, self.branches)
        self.info = info.GoosvcInfo(self.projects_dir, self.nodes, self.artifacts, self.stages, self.chats, self.messages, self.branches)

    def get_base_dir(self):
        return self.base_dir
    
 