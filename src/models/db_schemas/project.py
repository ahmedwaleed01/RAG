from pydantic import BaseModel,Field,validator,ConfigDict
from typing import Optional
from bson.objectid import ObjectId


class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)


    @validator("project_id")
    def validate_project_id(cls, v):
        if not v.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return v
    
    model_config = ConfigDict(arbitrary_types_allowed=True)