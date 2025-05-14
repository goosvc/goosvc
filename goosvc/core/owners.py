import os

class GoosvcOwners:
    def __init__(self, projects_dir: str):
        self.projects_dir = projects_dir
    
    def get_owners(self):
        return os.listdir(self.projects_dir)
