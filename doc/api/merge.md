# Merging


## Execute a merge
`merge` executes a merge operation for a given list of node or branch ids.
```
# node or branch ids to merge
head_ids = ['....','....','....']

branch_id, node_id = gvc.merge(OWNER, PROJECT, USER, head_ids)

if branch_id:
    print("Merge executed successfully")
```