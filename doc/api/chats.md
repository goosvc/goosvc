# Chats

## Creating an empty chat

If no parent it given, a new empty chat is created. Empty means that the new chat will not contain any messages.
```
# create a chat with no parent named "first chat", no parent chat node
chat = GoosvcChat(USER, "first chat") 

# id if it's the first node in the project. Use branch id otherwise
id = None

branch_id, _, chat_id_1 = gvc.create_chat(OWNER, PROJECT, id, chat)
```
The chat name is for documentation only and not necessarily unique. For adding messages to the chat you need the chat id.

## Reading exiting chats
`get_chats` return a list with all existing chats for a given branch and project.
```
existing_chats = gvc.get_chats(OWNER, PROJECT, branch_id)
print(existing_chats)
```
```
[{
    'chat_name': 'first chat', 
    'chat_id': '...', 
    'parent_chat_node_id': None
}]
```

## Creating a chat with a parent
When creating a chat, you can define any message from an existing chat as parent chat node. The new chat will then continue from this point without modifying the parent chat. Note: both chats co-exist in the same branch.

```
# create a new chat with message_id_1 as parent
chat = GoosvcChat(USER, "chat 1 version 2", message_id_1)
branch_1, _, chat_id_2 = gvc.create_chat(OWNER, PROJECT, branch_1, chat)
```

## Example: Using multiple chats in parallel
```
# Create chat 1
chat = GoosvcChat(USER, "first chat") 
branch_id, _, chat_id_1 = gvc.create_chat(OWNER, PROJECT, None, chat)

# add a message to chat 1 (that will be used by both chats)
message = GoosvcMessage(USER, "Which is the capital of France?", "Paris", chat_id_1)
branch_id, message_id_1 = gvc.add_message(OWNER, PROJECT, branch_id, message)

# add another message to chat 1
message = GoosvcMessage(USER, "Which is the capital of Germany?", "Berlin", chat_id_1)
branch_id, _ = gvc.add_message(OWNER, PROJECT, branch_id, message)

# create chat 2. Use message_id_1 as parent
chat = GoosvcChat(USER, "first chat", message_id_1) 
branch_id, _, chat_id_2 = gvc.create_chat(OWNER, PROJECT, branch_id, chat)

# add message to chat 2
message = GoosvcMessage(USER, "Do you like such questions?", "No, they are boring.", chat_id_2)
branch_id, _ = gvc.add_message(OWNER, PROJECT, branch_id, message)
```
Reading the chats
```
messages_1 = gvc.get_messages(OWNER, PROJECT, chat_id_1, branch_id)
print("Chat 1:\n",messages_1)
messages_2 = gvc.get_messages(OWNER, PROJECT, chat_id_2, branch_id)
print("Chat 2:\n",messages_2)
```
```
Chat 1:
  [{
    "user": "...", 
    "request" : "Which is the capital of France?", 
    "response": "Paris"
  },{
    "user": "...", 
    "request" : "Which is the capital of Germany?", 
    "response": "Berlin"
  }]
Chat 2:
  [{
    "user": "...", 
    "request" : "Which is the capital of France?", 
    "response": "Paris"
  },{
    "user": "...", 
    "request" : "Do you like such questions?", 
    "response": "No, they are boring."
  }]```
