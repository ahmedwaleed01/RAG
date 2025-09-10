from .BaseDataModel import BaseDataModel
from models.db_schemas import DataChunk
from .enums import DatabaseEnum


class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_CHUNK.value]
    
    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk.id = result.inserted_id
        return chunk
    
    async def get_chunk(self, chunk_id: str):
        chunk = await self.collection.find_one({"_id": chunk_id})
        if chunk is not None:
            return DataChunk(**chunk)
        return None
    
    ### I need to write chunks by patches (bulk)
    # async def insert_many_chunks(self, chunks: list,batch_size: int = 100):
        