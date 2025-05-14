# Messages


## Adding messages to a chat
```
ASSISTANT = ChatGPT

# add message(s) to chat 1
message = GoosvcMessage(USER, "Which is the capital of France?", "Paris", chat_id_1, ASSISTANT)
branch_id, message_id = gvc.add_message(OWNER, PROJECT, branch_id, message)

# add more messages...
```
Note: the chat_id must exist within the current branch.


## Adding messages with artifacts
```
# store artifacts
branch_id, input_fig_1 = self.gvc.store_artifact(...)
branch_id, output_fig_1 = self.gvc.store_artifact(...)
branch_id, output_fig_2 = self.gvc.store_artifact(...)

request_artifacts = {"person": input_fig_1}
response_artifacts = {"picture_before": output_fig_1, "picture_after": output_fig_2}

# add message(s) to chat 1
message = GoosvcMessage(USER, "Can you generate two images showing spectators at a football match? One before the goal, one after the goal. One of the spectators should be the person in the following picture.", "Done", chat_id_1, ASSISTANT, request_artifacts, response_artifacts)
branch_id, message_id = gvc.add_message(OWNER, PROJECT, branch_id, message)

# add more messages...
```
Note: the chat_id must exist within the current branch.

## Reading messages from a chat
```
messages = gvc.get_messages(OWNER, PROJECT, chat_id_1, branch_1)
print(messages)
```



