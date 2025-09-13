from fastapi import APIRouter, Depends , FastAPI, UploadFile , status,Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController,ProcessController
import aiofiles
from models import ResponeseEnum,ProjectModel,ChunkModel
from models.db_schemas.data_chunk import DataChunk
from .schemas.data import ProcessRequest


data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request:Request,project_id: str, file: UploadFile,
                       app_settings: Settings = Depends(get_settings)):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
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
async def process_data(request:Request,project_id: str, process_request: ProcessRequest,
                       app_settings: Settings = Depends(get_settings)):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    reset = process_request.reset

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

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
    
    if reset:
        _  = await chunk_model.delete_chunks_by_projectId(project_id=project.id)

    file_chunks_record = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadat=chunk.metadata,
            chunk_order=index + 1,
            chunk_project_id=project.id
        )
        for index, chunk in enumerate(file_chunks)
    ]

    chunks_len = await chunk_model.insert_many_chunks(chunks=file_chunks_record)
 

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "no_of_chunks": chunks_len
        }
    )
