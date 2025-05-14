import os
import uuid
import hashlib
import time


def get_project_dir(projects_dir: str, owner: str, project: str):
    return os.path.join(projects_dir, owner, project) 

def get_id():
    return uuid.uuid4().hex

def is_id_valid(id: str):
    return len(id) == 32 and id.isalnum()

def get_file_hash(artifact_file):
    hash_md5 = hashlib.md5()
    with open(artifact_file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_artifact_file(projects_dir: str, owner: str, project: str, artifact_id: str):
    project_dir = get_project_dir(projects_dir, owner, project)
    return os.path.join(project_dir, "artifacts", artifact_id)  # path to artifact file

def get_timestamp():
    return int(time.time())

