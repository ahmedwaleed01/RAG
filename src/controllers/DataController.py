from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponeseEnum
import os
import re



class DataController(BaseController):

    def __init__(self):
        super().__init__()
    
    def validate_file(self, file: UploadFile):

        if file.content_type not in self.app_settings.FILE_ALLOWED_EXTENSIONS:
            return False, ResponeseEnum.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE:
            return False, ResponeseEnum.FILE_SIZE_EXCEEDED.value
        
        return True, ResponeseEnum.FILE_VALIDATED_SUCCESS.value
    
    def generate_filepath(self,project_id: str, filename: str) -> str:

        random_key = self.generate_random_string()
  
        project_dir = ProjectController().get_projectPath(project_id)
        
        cleaned_filename = self.get_cleaned_filename(filename)

        file_path = os.path.join(project_dir, random_key+'_'+cleaned_filename)

        while os.path.exists(file_path):
            random_key = self.generate_random_string()
            file_path = os.path.join(project_dir, random_key+'_'+cleaned_filename)
  
        return file_path , random_key+'_'+cleaned_filename
    
    def get_cleaned_filename(self, orig_file_name: str) -> str:
        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        cleaned_file_name = re.sub(r'\s+', '_', cleaned_file_name)

        return cleaned_file_name
        