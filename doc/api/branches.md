# Branches

Branches are created automatically when adding nodes. There are no specific API function to create branches. New branches are created automatically whenever a node is added with a parent that is not the head id of any existing branch.

## Getting all branche ids
`get_branches` returns a list with all branches ids of a project.

```
branches = gvc.get_branches(OWNER, PROJECT)
print(branches)
```
Example output for a project with two branches:
```
['38e13fe73a204c37a942bb787fc78529','85eba8d099aa4f7398a4caa895115a55']
```

## Getting the head node id of a branch
`get_branch_head` returns the node id of the head node for a given branch id. Example to read the id of the head node of the first branch.
```
head_1 = gvc.get_branch_head(OWNER, PROJECT, branches[0])
print(head_1)
```

## Getting all branch heads ids
`get_heads` returns a list with all branch heads of a project.
```
heads = gvc.get_heads(OWNER, PROJECT)
print(heads)
```


 