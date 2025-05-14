import os
import json
from dataclasses import dataclass
import dataclasses
import shutil
import threading
from goosvc.core import common as common
from goosvc.core.owners import GoosvcOwners
from goosvc.core.exceptions import GoosvcException


DEFAULT_PROJECT_LOCK_TIMEOUT = 10 # seconds. set to -1 for infinite timeout
DEFAULT_OWNER_LOCK_TIMEOUT = 10 # seconds. set to -1 for infinite timeout

@dataclass
class GoosvcProject:
    name: str
    owner: str
    users: dict
    description: str = ""
    private: bool = True

@dataclass
class GoosvcPermission:
    read: bool
    write: bool
    admin: bool

class GoosvcProjects:
    def __init__(self, projects_dir: str, owners: GoosvcOwners):
        # base folder for all projects
        self.projects_dir = projects_dir
        self.owners = owners
        # create individual locks for all projects and owners
        self.owner_lock_timeout = DEFAULT_OWNER_LOCK_TIMEOUT
        self.owner_locks = {}
        self.project_lock_timeout = DEFAULT_PROJECT_LOCK_TIMEOUT
        self.project_locks = {}
        projects = self.get_all_project_names()
        for owner in projects:
            self.owner_locks[owner] = threading.Lock()
            self.project_locks[owner] = {}
            for project in projects[owner]:
                self.project_locks[owner][project] = threading.Lock()
        # load all projects to memory
        self.projects = {}
        for owner in projects:
            self.projects[owner] = {}
            for project in projects[owner]:
                self.projects[owner][project] = self.read_project(owner, project)

    def get_all_project_names(self): 
        projects = {}
        for owner in self.owners.get_owners():
            projects[owner] = self.get_project_names(owner)
        return projects
    
    def get_project_names(self, owner): 
        user_dir = os.path.join(self.projects_dir, owner)
        if not os.path.exists(user_dir):
            return []
        return os.listdir(user_dir)
    
    def get_public_project_names(self, owner): 
        user_dir = os.path.join(self.projects_dir, owner)
        if not os.path.exists(user_dir):
            return []
        projects = os.listdir(user_dir)
        public_projects = []
        for project in projects:
            project_file = self.__get_project_file(owner, project)
            with open(project_file, 'r') as f:
                project_obj = GoosvcProject(**json.load(f))
                if not project_obj.private:
                    public_projects.append(project)
        return public_projects
        
    def set_access_permission(self, owner: str, project: str, user: str, permission: GoosvcPermission):
        if user == owner: # owner has full access. cannot be changed
            raise GoosvcException("1010") 
        if len(user) < 4 or not user.replace('_', '').isalnum(): # invalid user name
            raise GoosvcException("1007") 
        if not owner in self.projects or not project in self.projects[owner]: # project not found
            raise GoosvcException("1001") 
        if not self.lock_project(owner, project): # no concurrent write access to project file
            raise GoosvcException("1003")
        # set permission in memory
        self.projects[owner][project].users[user] = permission
        # write permission to file
        self.write_project(owner, project, self.projects[owner][project])
        self.release_project(owner, project)
        return True
    
    def get_access_permission(self, owner: str, project: str, user: str):
        if not owner in self.projects or not project in self.projects[owner]:
            # project does not exist
            return GoosvcPermission(False, False, False)
        if user == "app": # app has full access
            return GoosvcPermission(True, True, True)
        if user in self.projects[owner][project].users:
            permission = self.projects[owner][project].users[user]
            if (type(permission) == GoosvcPermission):
                return permission
            return GoosvcPermission(**permission) 
        if not self.projects[owner][project].private:
            return GoosvcPermission(True, False, False)
        return GoosvcPermission(False, False, False)
    
    def set_private(self, owner: str, project: str, private: bool):
        if not owner in self.projects or not project in self.projects[owner]:
            return False
        if not self.lock_project(owner, project): # no concurrent write access to project file
            return False
        # set permission in memory
        self.projects[owner][project].private = private
        # write permission to file
        self.write_project(owner, project, self.projects[owner][project])
        self.release_project(owner, project)
        return True
    
    def create_project(self, owner: str, project_name: str, project_description: str = ""):
        user_dir = os.path.join(self.projects_dir, owner)
        if not self.lock_owner(owner): # make sure owner is not creating multiple projects at the same time
            raise GoosvcException("1003")
        if not os.path.exists(user_dir):
            # check if owner is valid
            if len(owner) < 4 or not owner.replace('_', '').isalnum():
                # print(owner)
                self.release_owner(owner)
                raise GoosvcException("1007")
            # create user directory if it does not exist
            os.makedirs(user_dir)
        projects = self.get_project_names(owner)
        if project_name in projects:
            # Project already exists
            self.release_owner(owner)
            raise GoosvcException("1005")
        if len(project_name) < 4 or not project_name.replace('_', '').isalnum():
            # print(project_name)
            self.release_owner(owner)
            raise GoosvcException("1006")
        project_dir = common.get_project_dir(self.projects_dir, owner, project_name)
        os.makedirs(project_dir)
        nodes_dir = os.path.join(project_dir, "nodes")
        os.makedirs(nodes_dir)
        aritfacts_dir = os.path.join(project_dir, "artifacts")
        os.makedirs(aritfacts_dir)
        branches_dir = os.path.join(project_dir, "branches")
        os.makedirs(branches_dir)
        branchgroups_dir = os.path.join(project_dir, "branchgroups")
        os.makedirs(branchgroups_dir)
        project_obj = GoosvcProject(project_name, owner, {owner: GoosvcPermission(True, True, True)}, project_description)
        self.write_project(owner, project_name, project_obj)
        # create lock for project
        if owner not in self.project_locks:
            self.project_locks[owner] = {}
        self.project_locks[owner][project_name] = threading.Lock()
        # add project to memory
        if not owner in self.projects:
            self.projects[owner] = {}
        self.projects[owner][project_name] = project_obj
        self.release_owner(owner)
        return True
    
    #  only used during startup (no lock required)
    def read_project(self, owner: str, project_name: str):
        project_file = self.__get_project_file(owner, project_name)
        with open(project_file, 'r') as f:
            return GoosvcProject(**json.load(f))
        
    # caller should lock project if its not a new project
    def write_project(self, owner: str, project_name: str, project: GoosvcProject):
        project_file = self.__get_project_file(owner, project_name)
        with open(project_file, 'w') as f:
            f.write(json.dumps(dataclasses.asdict(project)))
    
    def get_project(self, owner: str, project_name: str):
        if not owner in self.projects or not project_name in self.projects[owner]:
            return None
        return self.projects[owner][project_name]
    
    def delete_project(self, owner: str, project_name: str):
        if not self.lock_project(owner, project_name): # stop all write access to project
            return False
        projects = self.get_project_names(owner)
        if project_name not in projects:
            # Project does not exist
            return False
        project_dir = common.get_project_dir(self.projects_dir, owner, project_name)
        if not self.__is_project_dir(owner, project_name):
            return False
        #  delete project directory
        shutil.rmtree(project_dir)
        # remove lock
        if owner in self.project_locks and project_name in self.project_locks[owner]:
            del self.project_locks[owner][project_name]
        return True
    
    def lock_project(self, owner: str, project: str):
        if owner not in self.project_locks:
            self.project_locks[owner] = {}
        if project not in self.project_locks[owner]:
            self.project_locks[owner][project] = threading.Lock()
        # print("***** Locking project", owner, project)
        return self.project_locks[owner][project].acquire(timeout=self.project_lock_timeout)

    def release_project(self, owner: str, project: str):
        if owner not in self.project_locks:
            print("Error: owner not in locks")
            return
        if project not in self.project_locks[owner]:
            print("Error: project not in locks")
            return
        # print("****** Releasing Project", owner, project)
        self.project_locks[owner][project].release()
    
    def lock_owner(self, owner: str):
        if owner not in self.owner_locks:
            self.owner_locks[owner] = threading.Lock()
        # print("***** Locking owner", owner)
        return self.owner_locks[owner].acquire(timeout=self.owner_lock_timeout)
    
    def release_owner(self, owner: str):
        if owner not in self.owner_locks:
            print("Error: owner not in locks")
            return
        # print("****** Releasing Owner", owner)
        self.owner_locks[owner].release()
    
    def lock_all_projects_of_owner(self, owner: str):
        projects = self.get_project_names(owner)
        while len(projects) > 0:
            for project in projects:
                if self.lock_project(owner, project):
                    # print("Locked", project)
                    projects.remove(project)
            # print("Lock is pending for", projects)
        # print("Locked all projects of", owner)
            
    def release_all_projects_of_owner(self, owner: str):
        projects = self.get_project_names(owner)
        for project in projects:
            self.project_locks[owner][project].release()
    
    def lock_all_projects(self):
        for owner in self.get_all_project_names():
            # print("++++ Locking all projects of", owner)
            self.lock_all_projects_of_owner(owner)

    def release_all_projects(self):
        for owner in self.get_all_project_names():
            self.release_all_projects_of_owner(owner)
    
    def __get_project_file(self, owner: str, project: str):
        project_dir = common.get_project_dir(self.projects_dir, owner, project)
        return os.path.join(project_dir, "project.json")
    
    def __is_project_dir(self, owner: str, project: str):
        # TODO: check if it only contains the required directories
        return os.path.exists(self.__get_project_file(owner, project))

