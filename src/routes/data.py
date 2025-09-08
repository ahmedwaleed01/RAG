from fastapi import APIRouter, Depends , FastAPI, UploadFile
from helpers import get_settings, Settings
from controllers import DataController

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile,
                       app_settings: Settings = Depends(get_settings)):
    
    # validate file type
    data_controller = DataController()

    is_valid, message = data_controller.validate_file(file)

    return {"is_valid": is_valid, "message": message}
    
 
    # # get file directory

    # pass