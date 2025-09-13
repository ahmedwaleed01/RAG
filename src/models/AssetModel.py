from .BaseDataModel import BaseDataModel
from .db_schemas import Asset
from .enums import DatabaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):

    _instance = None

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_ASSET.value]
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DatabaseEnum.COLLECTION_ASSET.value not in all_collections:
            self.collection = self.db_client[DatabaseEnum.COLLECTION_ASSET.value]
            indexes = Asset.get_indexes()
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
    
    # create Asset
    async def create_asset(self, asset: Asset):
        ## convert pydantic model to dict to be understood by motors and insert into mongodb
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset
    
    # get all assets by project id
    async def get_all_assets_by_project_id(self, project_id: str , asset_type :str):
      records = await self.collection.find({
          "asset_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id,
          "asset_type": asset_type
      }).to_list(length=None)

      return [Asset(**record) for record in records]
    
    # get asset by asset name and project id
    async def get_asset_by_name_and_project_id(self, asset_name: str, project_id: str):
        record = await self.collection.find_one({
            "asset_name": asset_name,
            "asset_project_id": ObjectId(project_id) if isinstance(project_id, str) else project_id
        })
        if record:
            return Asset(**record)
        return None

