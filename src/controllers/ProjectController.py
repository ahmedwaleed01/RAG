from .BaseController import BaseController
import os
from fastapi import HTTPException, status

class ProjectController(BaseController):
    def __init__(self):
        super().__init__()

    def get_projectPath(self, project_id: str) -> str:
        project_id = self.sanitize_id(project_id)

        project_dir = os.path.abspath(os.path.join(self.files_dir, project_id))
        if not project_dir.startswith(os.path.abspath(self.files_dir) + os.sep):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid project_id")

        if not os.path.exists(project_dir):
            os.makedirs(project_dir, exist_ok=True)

        return project_dir