from enum import Enum

class Datastore_type(str, Enum):
    POSTGRES = "POSTGRES",
    ELASTICSEARCH = "ELASTICSEARCH",
    COLLECTORAPI = "COLLECTORAPI",

