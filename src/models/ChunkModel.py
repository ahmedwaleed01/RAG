from bson import ObjectId
from .BaseDataModel import BaseDataModel
from models.db_schemas import DataChunk
from .enums import DatabaseEnum
from pymongo import InsertOne


class ChunkModel(BaseDataModel):
    _instance = None

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_CHUNK.value]
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_CHUNK.value not in all_collections:
            self.collection = self.db_client[DatabaseEnum.COLLECTION_CHUNK.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name = index['name'],
                    unique = index['unique'],
                )
    @classmethod
    async def create_instance(cls, db_client):
        if cls._instance is None:
            instance = cls(db_client)
            await instance.init_collection()
            cls._instance = instance
        return cls._instance
    
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
    async def insert_many_chunks(self, chunks: list,batch_size: int = 100):

        for i in range (0,len(chunks),batch_size):
            batch = chunks[i:i+batch_size]

            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)
    

    async def delete_chunks_by_projectId(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
        
    async def get_project_chunks(self, project_id: ObjectId, page_number:int = 1, page_size:int =50):
        result = await self.collection.find({
            "chunk_project_id":  project_id
        }).skip((page_number-1)*page_size).limit(page_size).to_list(length=None)

        return [
            DataChunk(**res)
            for res in result
        ]
        