# Setup

## Connecting with the Python API

```
from goosvc import *

gvc = Goosvc("......") # Add path to repository
```


GOOSVC needs a folder in the file system to store the repository. If no path is given, GOOSVC searches for a folder named "data" in the current root directory. If such a folder exist, it will be used as repository. If it does not exist, a new folder named 'data' is created.

You should not start multiple instances of GOOSVC using the same repository. This will create conflicts. Running multiple instances on the same system on different repositories is fine. Its also fine to start multiple threads using the same instance of GOOSVC. The system prevents simultaneous access to vulnerable section with locks (here, a reference should be added describing this in detail). 

## Shutting down
When the GOOSVC is stopped, all write operations must be completed. For this, you should lock all projects before shut down. 

```
gvc.lock_all_projects()
```
The function will return after all projects have been locked successfully.
