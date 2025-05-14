import os
import time
import json
from goosvc.core import common as common
from dataclasses import dataclass
import dataclasses
from goosvc.core.projects import GoosvcProjects


HEADREAD_MAX_RETRY = 100
DEFAULT_BRANCH_HEAD_CACHE_SIZE = 1000

@dataclass
class BranchGroup:
    branch_ids: list
    description: str = None
    group_id: str = None


# For all functions we assume that the node_id is a valid node_id. 
# Should be checked before calling the functions
class GoosvcBranches:
    def __init__(self, projects_dir: str, projects: GoosvcProjects):
        self.projects_dir = projects_dir
        self.projects = projects
        # path cache by owner and project
        self.branch_head_cache = {}
        self.branch_head_cache_size = DEFAULT_BRANCH_HEAD_CACHE_SIZE

    def get_branches(self, owner: str, project: str):
        branches_dir = self.__get_branches_dir(owner, project)
        if not os.path.exists(branches_dir):
            return []
        branch_files = os.listdir(branches_dir)
        branch_ids = [os.path.splitext(branch_file)[0] for branch_file in branch_files]
        return branch_ids
    
    def is_branch(self, owner: str, project: str, branch_id: str):
        if owner in self.branch_head_cache and project in self.branch_head_cache[owner]:
            if branch_id in self.branch_head_cache[owner][project]:
                return True
        branch_file = self.__get_branch_file(owner, project, branch_id)
        return os.path.exists(branch_file)
    
    #  to be removed (backward compatibility)
    def get_heads(self, owner: str, project: str):
        branches = self.get_branches(owner, project)
        heads = []
        for branch_id in branches:
            branch_head = self.get_branch_head(owner, project, branch_id)
            if branch_head == None:
                continue
            heads.append(branch_head)
        return heads
    
    def get_branch_head(self, owner: str, project: str, branch_id: str):
        if owner in self.branch_head_cache and project in self.branch_head_cache[owner]:
            if branch_id in self.branch_head_cache[owner][project]:
                # read from cache
                return self.branch_head_cache[owner][project][branch_id]
        # read from file
        branch_file = self.__get_branch_file(owner, project, branch_id)
        retry_count = 0
        while retry_count < HEADREAD_MAX_RETRY:
            retry_count += 1
            if not os.path.exists(branch_file):
                return None
            try:
                with open(branch_file, 'r') as f:
                    head_id = f.read()
                    if common.is_id_valid(head_id):
                        self.update_branch_head_cache(owner, project, branch_id, head_id)
                        return head_id
            except:
                pass
            time.sleep(0.01)

    def create_branch(self, owner: str, project: str, node_id: str):
        branch_id = common.get_id()
        branch_file = self.__get_branch_file(owner, project, branch_id)
        with open(branch_file, 'w') as f:
            # save to file
            f.write(node_id)
            # update cache
            self.update_branch_head_cache(owner, project, branch_id, node_id)
        return branch_id

    def update_branch_head(self, owner: str, project: str, branch_id: str, node_id: str):
        branch_file = self.__get_branch_file(owner, project, branch_id)
        if not os.path.exists(branch_file):
            return False
        with open(branch_file, 'w') as f:
            # save to file
            f.write(node_id)
            # update cache
            self.update_branch_head_cache(owner, project, branch_id, node_id)
        return True
    
    def update_branch_head_cache(self, owner: str, project: str, branch_id: str, node_id: str):
        if owner not in self.branch_head_cache:
            self.branch_head_cache[owner] = {}
        if project not in self.branch_head_cache[owner]:
            self.branch_head_cache[owner][project] = {}
        if branch_id in self.branch_head_cache[owner][project]:
            # remove old entry to make sure the new one is at the end
            del self.branch_head_cache[owner][project][branch_id]
        self.branch_head_cache[owner][project][branch_id] = node_id
        if len(self.branch_head_cache[owner][project]) > self.branch_head_cache_size:
            # remove oldest entry. sincy python 3.7 the order of keys is the same as the order of insertion
            oldest_branch_id = list(self.branch_head_cache[owner][project].keys())[0]
            del self.branch_head_cache[owner][project][oldest_branch_id]
    
    def get_branch_of_node(self, owner: str, project: str, node_id: str):
        branches = self.get_branches(owner, project)
        for branch_id in branches:
            branch_head = self.get_branch_head(owner, project, branch_id)
            if branch_head == node_id:
                return branch_id
        return None
    
    def create_branch_group(self, owner: str, project: str, branch_group: BranchGroup):
        # check if all branches exist
        branch_ids = branch_group.branch_ids
        for branch_id in branch_ids:
            if not self.is_branch(owner, project, branch_id):
                return None
        group_id = common.get_id()
        branch_group.group_id = group_id
        group_file = self.__get_group_file(owner, project, group_id)
        with open(group_file, 'w') as f:
            # save to file
            f.write(json.dumps(dataclasses.asdict(branch_group)))
        return group_id  
    
    def update_branch_group(self, owner: str, project: str, branch_group: BranchGroup):
        # check if all branches exist
        branch_ids = branch_group.branch_ids
        for branch_id in branch_ids:
            if not self.is_branch(owner, project, branch_id):
                return None
        group_id = branch_group.group_id
        group_file = self.__get_group_file(owner, project, group_id)
        # lock project to prevent concurrent access
        if not self.projects.lock_project(owner, project):
            return False
        if not os.path.exists(group_file):
            self.projects.release_project(owner, project)
            return False
        with open(group_file, 'w') as f:
            # save to file
            f.write(json.dumps(dataclasses.asdict(branch_group)))
        self.projects.release_project(owner, project)
        return True
    
    def get_branch_group(self, owner: str, project: str, group_id: str):
        group_file = self.__get_group_file(owner, project, group_id)
        if not os.path.exists(group_file):
            return None
        with open(group_file, 'r') as f:
            group_content = BranchGroup(**json.loads(f.read()))
            return group_content
    
    def get_branch_groups(self, owner: str, project: str):
        group_dir = self.__get_group_dir(owner, project)
        if not os.path.exists(group_dir):
            return []
        group_files = os.listdir(group_dir)
        group_ids = [os.path.splitext(group_file)[0] for group_file in group_files]
        return group_ids
    
    def __get_branches_dir(self, owner: str, project: str):
        project_dir = common.get_project_dir(self.projects_dir, owner, project)
        return os.path.join(project_dir, "branches")
    
    def __get_branch_file(self, owner: str, project: str, branch_id: str):
        branches_dir = self.__get_branches_dir(owner, project)
        return os.path.join(branches_dir, branch_id + ".json")
    
    def __get_group_dir(self, owner: str, project: str):
        project_dir = common.get_project_dir(self.projects_dir, owner, project)
        return os.path.join(project_dir, "branchgroups")
    
    def __get_group_file(self, owner: str, project: str, group_id: str):
        group_dir = self.__get_group_dir(owner, project)
        return os.path.join(group_dir, group_id + ".json")
