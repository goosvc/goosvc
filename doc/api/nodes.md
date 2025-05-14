# Nodes

Nodes can be added with the following API calls:

- [add chat](/doc/api/chats.md#creating-an-empty-chat)
- [add message](/doc/api/chats.md#adding-messages-to-a-chat)
- [store artifact](/doc/api/artifacts.md#storing-artifacts)
- [add stage](/doc/api/stages.md#adding-stages)
- [merge](/doc/api/merge.md)

Nodes are **immutable**, they cannot be edited or deleted.

## Reading a node
`get_node` returns the content of a node.
```
node = gvc.get_node(OWNER, PROJECT, node_id)
```

## Reading all nodes of a project version or branch
`get_path` returns a list with all nodes of a project starting from a specific node (id is a node id) or from the head of a branch (id is a branch id). 
```
nodes = gvc.get_path(OWNER, PROJECT, id)
``` 
`type` is an optional parameter to filter the nodes. Value must be a list containing all node types to be returned or None. For value None (the default value), all nodes are returned. 

The following  example returns all nodes of type chat and message:
```
nodes = gvc.get_path(OWNER, PROJECT, id, ['chat', 'message'])
``` 
`root_id` is an optional parameter to stop reading the path at the specified node. If the given root id is not found, all nodes are returned. If root id is None (the default value), all nodes are returned. 

The following example returns all nodes between id (included) and root_id (excluded):
```
nodes = gvc.get_path(OWNER, PROJECT, id, None, root_id)
``` 

## Reading all nodes of a project
`get_nodes` returns all nodes of a project.
```
nodes = gvc.get_nodes(OWNER, PROJECT)
``` 