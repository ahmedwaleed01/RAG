from enum  import Enum


class VectorDBEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"

class VectorDBProviderTypes(Enum):

    QDRANT = 'QDRANT'