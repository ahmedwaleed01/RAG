from fastapi import APIRouter, Depends , FastAPI, UploadFile , status
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController
import aiofiles
from models import ResponeseEnum

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

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": message
            }
        )

    file_path, file_id  = data_controller.generate_filepath(project_id, file.filename)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": ResponeseEnum.FILE_UPLOAD_FAILED.value,
            }
        )

    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "file_id": file_id
            }
        )
    