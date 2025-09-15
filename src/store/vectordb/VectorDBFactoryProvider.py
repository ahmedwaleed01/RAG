from .providers import QdrantDBProvider
from .VectorDBEnums import VectorDBProviderTypes
from ...helpers.config import Settings
from ...controllers.BaseController import BaseController

class VectorDBFactoryProvider:

    def __init__(self, config: Settings):
        self.config = config
        self.base_controller =  BaseController()
    
    def create(self, provider: str):
        if provider == VectorDBProviderTypes.QDRANT.value:
            vector_db_path = self.base_controller.get_database_path(self.config.VECTOR_DB_PATH)

            return QdrantDBProvider(
                db_path= vector_db_path,
                distance_method= self.config.VECTOR_DB_DISTANCE_METHOD
            )

        return None