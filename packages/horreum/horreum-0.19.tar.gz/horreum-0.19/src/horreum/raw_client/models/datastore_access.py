from enum import Enum

class Datastore_access(str, Enum):
    PUBLIC = "PUBLIC",
    PROTECTED = "PROTECTED",
    PRIVATE = "PRIVATE",

