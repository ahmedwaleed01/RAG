from helpers import get_settings, Settings
import os
import random
import string
import re
from fastapi import HTTPException, status


class BaseController:   
    def __init__(self):
        self.app_settings: Settings = get_settings()
        self.base_dir = os.path.dirname( os.path.dirname(__file__) )
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )

        self.vector_db_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )

    def generate_random_string(self, length: int=12):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def sanitize_id(self, value: str) -> str:
        if not value or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", value):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid id format")
        return value
    
    def get_database_path(self, db_name: str):

        db_path = os.path.join(
            self.vector_db_dir,
            db_name
        )

        if not os.path.exists(db_path):
            os.makedirs(db_path, exist_ok=True)

        return db_path