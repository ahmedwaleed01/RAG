from fastapi import APIRouter, Depends , FastAPI, UploadFile , status
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController,ProcessController
import aiofiles
from models import ResponeseEnum
from .schemas.data import ProcessRequest

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
@data_router.post("/process/{project_id}")
async def process_data(project_id: str, request: ProcessRequest,
                       app_settings: Settings = Depends(get_settings)):
    
    file_id = request.file_id
    chunk_size = request.chunk_size
    overlap_size = request.overlap_size
    reset = request.reset

    process_controller = ProcessController(project_id)

    file_content = process_controller.get_fileContent(file_id)

    file_chunks = process_controller.process_file_content(file_content=file_content,
                                                          chunk_size=chunk_size,overlap_size=overlap_size)
    
    if  file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponeseEnum.FILE_PROCESS_FAILED.value,
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "file_chunks": file_chunks
        }
    )