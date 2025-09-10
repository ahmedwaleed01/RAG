from .BaseDataModel import BaseDataModel
from .db_schemas import Project
from .enums import DatabaseEnum


class ProjectModel(BaseDataModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DatabaseEnum.COLLECTION_PROJECT.value]

    async def create_project(self, project: Project):
        result  =await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project._id = result.inserted_id
        return project
    
    async def get_project_or_create_one(self, project_id: str):
        project = await self.collection.find_one({"project_id": project_id})
        if project:
            return Project(**project)
        new_project = Project(project_id=project_id)
        created_project = await self.create_project(new_project)
        return created_project
    
    async def get_all_projects(self,page:int,page_size:int):
        # calculate total pages
        total_pages = await self.collection.count_documents({})
        total_pages = (total_pages + page_size - 1) // page_size
        if total_pages % page_size != 0:
            total_pages += 1

        skips = page_size * (page - 1)
        cursor = self.collection.find().skip(skips).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(Project(**document))
        return projects,total_pages