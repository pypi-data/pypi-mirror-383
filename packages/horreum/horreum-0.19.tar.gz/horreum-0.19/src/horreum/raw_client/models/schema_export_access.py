from enum import Enum

class SchemaExport_access(str, Enum):
    PUBLIC = "PUBLIC",
    PROTECTED = "PROTECTED",
    PRIVATE = "PRIVATE",

