# Stages

A stage refers to one version of a project. Stages are immutable and  stage names are unique within any path of the project. It is not possible to modify or delete stages. Stages cannot be merged.

## Adding a stage
`add_stage` adds a stage at for at specif verions (id is a node id) or at the current the head of a branch (id is a branch id). It return branch id an node id if the stage was created successfully and None elsewise.
```
USER = "marc"  # user creating the stage

stage = GoosvcStage(USER, "First Stage Name", "First stage description")
branch_id, node_id = gvc.add_stage(OWNER, PROJECT, id, stage)

if branch_id:
    print("Stage added successfully")
```

## Get all stage names for a given version or branch
`get_stage_names` returns a list with all stage names in the version history starting from a specific node (id is a node id) or from the head of a branch (id is a branch id). 
```
id = branch_id

stages = gvc.get_stage_names(OWNER, PROJECT, id)
print(stages)
```
```
['First Stage Name']
```

## Reading a stage
`get_stage_node` returns the stage node for a given stage name for the version or branch defined by the id or None, if the stage was not found.
```
stage_name = "First Stage Name"

stage_node = gvc.get_stage_node(OWNER, PROJECT, id, stage_name)
print(stage_node)
```
```
GoosvcNode(
    type='stage', 
    parent_id='...', 
    author='sue', 
    node_id='...', 
    timestamp=..., 
    version=6
    content={
        'stage_name': 'First Stage Name', 
        'stage_description': 'First stage description'
    })
```

`root_id` is an optional parameter to stop searching the history at the specified node. It is used to get all stages within a certain range of the projects history. If the given root id is not found or if its None (the default value), searching for the stage does not stop before finding the stage or reaching the first node of the project. 
```
stage_node = gvc.get_stage_node(OWNER, PROJECT, id, stage_name, root_id)
```

