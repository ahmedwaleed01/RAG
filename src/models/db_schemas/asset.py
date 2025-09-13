from datetime import datetime
from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from bson.objectid import ObjectId

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_name: str = Field(...,min_length=1)
    asset_type: str = Field(...,min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config: dict = Field(default=None)
    asset_pushed_at: datetime = Field(default=datetime.utcnow)
    asset_project_id : ObjectId

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def get_indexes(cls):
        
        return [
            {
                "key":[("asset_project_id",1)],
                "name":"asset_project_id_index_1",
                "unique":False
            }, 
            {
                "key":[("asset_name",1),("asset_project_id",1)],
                "name":"asset_name_project_id_index_1",
                "unique":True
            }
        ]