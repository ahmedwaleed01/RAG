from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponeseEnum
import os




class DataController(BaseController):

    def __init__(self):
        super().__init__()
    
    def validate_file(self, file: UploadFile):

        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponeseEnum.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.MAX_FILE_SIZE:
            return False, ResponeseEnum.FILE_SIZE_EXCEEDED.value
        
        return True, ResponeseEnum.FILE_VALIDATED_SUCCESS.value
    
    def generated_file_path(self,project_id: str, filename: str) -> str:
  
        project_dir = ProjectController().get_projectPath(project_id)
        file_path = os.path.join(project_dir, filename)
  
        return file_path