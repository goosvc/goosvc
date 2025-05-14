# Transactions

## Store message with artifacts within a transaction
```
# start transaction
transaction = transactions.GoosvcTransaction(USER)
branch_id, _, transaction_id = self.gvc.start_transaction(OWNER, PROJECT, branch_id, transaction)

# store artifacts, use transaction id
artifact1 = StoreFileArtifact(..., ORIGIN1, transaction_id)
branch_id, input_fig_1 = self.gvc.store_artifact(...,artifact1)
artifact2 = StoreFileArtifact(..., ORIGIN2, transaction_id)
branch_id, output_fig_1 = self.gvc.store_artifact(...,artifact2)
artifact3 = StoreFileArtifact(..., ORIGIN2, transaction_id)
branch_id, output_fig_2 = self.gvc.store_artifact(...,artifact3)

request_artifacts = {"person": input_fig_1}
response_artifacts = {"picture_before": output_fig_1, "picture_after": output_fig_2}

# add message(s) to chat 1
message = GoosvcMessage(USER, "Can you generate two images showing spectators at a football match? One before the goal, one after the goal. One of the spectators should be the person in the following picture.", "Done", chat_id_1, ASSISTANT, request_artifacts, response_artifacts, transaction_id)
branch_id, message_id = gvc.add_message(OWNER, PROJECT, branch_id, message)

# end transaction
transaction = transactions.GoosvcTransaction(USER, transaction_id)
branch_id, _, _ = self.gvc.end_transaction(OWNER, PROJECT_NAME, branch_id, transaction)
```




