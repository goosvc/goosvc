# Artifacts

## Storing an artifact
`store_artifact` adds one artifact at the position indicated by id to the chat referenced by chat_id
```
FILE_NAME = "picture.png"
PATH = "pictures/figure_1"
input_file = "figure1.png"  

artifact = StoreFileArtifact(USER, FILE_NAME, PATH, input_file)
branch_id, node_id = gvc.store_artifact(OWNER, PROJECT, id, chat_id, artifact)

if branch_id:
    print("Artifact stored successfully")
```
`origin` is an optional parameter to declare the origin of an artifact. The application can decide how to uses this field. Examples:
```
origin = "external"
artifact = StoreFileArtifact(USER, FILE_NAME, PATH, input_file, origin)

origin = {"message": "70ad4b79e9a04413b50c72642ce38844"}
artifact = StoreFileArtifact(USER, FILE_NAME, PATH, input_file, origin)
```

## Reading all artifact nodes 
`get_artifact_nodes` returns all artifact nodes visible for the version or branch indicated by id.
```
artifact_nodes = gvc.get_artifact_nodes(OWNER, PROJECT, id)
print(artifact_nodes)
```
```
[GoosvcNode(
    type='artifact', 
    parent_id='...', 
    author='sue', 
    node_id='...', 
    timestamp=..., 
    version=7,
    content={
        'artifact_id': '...', 
        'chat_id': '...', 
        'operation': 'add', 
        'filename': 'picture.png', 
        'path': 'pictures/figure_1', 
        'filehash': '...', 
        'media_type': 'image/png'
    })]
```

## Deleting an artifact
`delete_artifact` deletes an artifact by adding an artifact node with operation delete.
```
artifact = DeleteArtifact(USER, FILE_NAME, PATH)

branch_id, node_id = gvc.delete_artifact(OWNER, PROJECT, id, , chat_id, artifact)

if branch_id:
    print("Artifact deleted successfully")
```
```
artifact_nodes = gvc.get_artifact_nodes(OWNER, PROJECT, id)
print(artifact_nodes)
```
```
[GoosvcNode(
    type='artifact', 
    parent_id='...', 
    author='sue', 
    node_id='...', 
    timestamp=..., 
    version=8,
    content={
        'artifact_id': None, 
        'chat_id': '...', 
        'operation': 'delete', 
        'filename': 'picture.png', 
        'path': 'pictures/figure_1', 
        'filehash': None, '
        media_type': None}
    )]

```



