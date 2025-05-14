# Projects

## Creating a new project

After [connecting with the Python-API](/doc/api/setup-core.md), a project can be created.

```
PROJECT = "demo"
OWNER = "paul"

# create a project. 
response = gvc.create_project(OWNER,PROJECT,"This is a demo project")

if response:
    print("Project created")
```
```
Project created
```

Owner and project names must be at least 4 characters long. Only alphanumeric characters and underscores are allowed. `create_project` returns true if the project was created successfully. If the owner does not exist, it is created along with the project. The project owner automatically gets read, write and admin permissions. More users can be added later.

## List existing projects
`get_project_names` returns a list of all projects of the given owner.
```
projects = gvc.get_project_names(OWNER)
print(projects)
```
```
['demo']
```

## Delete a project
`delete_project` returns true if the project was deleted successfully.
```
response = gvc.delete_project(OWNER, PROJECT)
if response:
    print("Project deleted")
```

## Getting project details
```
details = gvc.get_project(OWNER, PROJECT)
print(details)
```
```
GoosvcProject(
    name='demo', 
    owner='paul', 
    users={'paul': {'read': True, 'write': True, 'admin': True}}, 
    description='This is a demo project', 
    private: True
)
```

## Adding and updating users
```
USER_NAME = "sue"
user_permission = GoosvcPermission(read=True, write=True, admin=False)

gvc.set_access_permission(OWNER_NAME, PROJECT_NAME, USER_NAME, user_permission)
```  
Permissions of the project owner are immutable. 

## Making a project public
Set private to false to make the project public. This gives all users read permission.
```
self.gvc.set_private(OWNER_NAME, PROJECT_NAME, False)
```