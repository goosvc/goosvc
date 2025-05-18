import json

class GoosvcException(Exception):
    def __init__(self, code: str):  
        self.code = code
        if code in self.goosvc_exceptions:
            self.status = self.goosvc_exceptions[code]["status"]
            self.message = self.goosvc_exceptions[code]["message"]
            self.type = self.goosvc_exceptions[code]["type"]
        else:
            self.status = "error"
            self.message = "Error in request."
            self.type = "BAD_REQUEST"
            
    def __str__(self):
        response = {"status": self.status, "message": self.message, "code": self.code, "type": self.type}
        return json.dumps(response)
    
    goosvc_exceptions = {
        "1000": {"status": "error", "message": "Error in request.", "type": "BAD_REQUEST"},
        # project errors
        "1001": {"status": "error", "message": "Project not found.", "type": "NOT_FOUND"},
        "1002": {"status": "error", "message": "You don't have permission to access this project", "type": "FORBIDDEN"},
        "1003": {"status": "error", "message": "Project locked.", "type": "LOCKED"},
        "1004": {"status": "error", "message": "You can not create projects for other users.", "type": "FORBIDDEN"},
        "1005": {"status": "error", "message": "Project already exists.", "type": "BAD_REQUEST"},
        "1006": {"status": "error", "message": "Project name must be at least 4 characters and can only contain alphanumeric characters and underscores.", "type": "BAD_REQUEST"},
        "1007": {"status": "error", "message": "Username must be at least 4 characters long and can only contain alphanumeric characters and underscores.", "type": "BAD_REQUEST"},
        "1008": {"status": "error", "message": "You don't have permission to administrate this project", "type": "FORBIDDEN"},
        "1009": {"status": "error", "message": "You don't have permission to edit this project", "type": "FORBIDDEN"},
        "1010": {"status": "error", "message": "Access permissions of owner is immutable", "type": "BAD_REQUEST"},
        "1011": {"status": "error", "message": "Internal server error.", "type": "INTERNAL_SERVER_ERROR"},
        "1012": {"status": "error", "message": "Branch not found.", "type": "BAD_REQUEST"},
        "1013": {"status": "error", "message": "Invalid parent chat node id.", "type": "BAD_REQUEST"},
        "1014": {"status": "error", "message": "Parent chat node is not a message node.", "type": "BAD_REQUEST"},
        "1015": {"status": "error", "message": "Stage name already exists.", "type": "BAD_REQUEST"},
        "1016": {"status": "error", "message": "Chat not found.", "type": "BAD_REQUEST"},
        "1017": {"status": "error", "message": "Artifact already exists in another chat and is marked as global.", "type": "BAD_REQUEST"},
        "1018": {"status": "error", "message": "Invalid input file.", "type": "BAD_REQUEST"},
        "1019": {"status": "error", "message": "Input file is empty.", "type": "BAD_REQUEST"},
        "1020": {"status": "error", "message": "Input file too big.", "type": "BAD_REQUEST"},
        "1021": {"status": "error", "message": "Invalid path.", "type": "BAD_REQUEST"},
        "1022": {"status": "error", "message": "Invalid filename.", "type": "BAD_REQUEST"},
        "1023": {"status": "error", "message": "Message not found.", "type": "BAD_REQUEST"},
        "1024": {"status": "error", "message": "Artifact not found.", "type": "BAD_REQUEST"},
        "1025": {"status": "error", "message": "Node not found.", "type": "BAD_REQUEST"},
        "1026": {"status": "error", "message": "Project locked by transaction.", "type": "LOCKED"},
        "1027": {"status": "error", "message": "Invalid transaction.", "type": "BAD_REQUEST"},
        "1028": {"status": "error", "message": "Banching refused. You can not branch off in the middle of a transaction.", "type": "BAD_REQUEST"},
        "1029": {"status": "error", "message": "Invalid parent.", "type": "BAD_REQUEST"},
        "1030": {"status": "error", "message": "Missing transaction id.", "type": "BAD_REQUEST"},
        "1031": {"status": "error", "message": "Invalid response", "type": "INTERNAL_SERVER_ERROR"},

    }


