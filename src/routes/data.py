import os
from fastapi import APIRouter, Depends , FastAPI, UploadFile , status,Request
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
from controllers import DataController,ProcessController
import aiofiles
from models import ResponeseEnum,ProjectModel,ChunkModel,AssetModel,AssetEnum
from models.db_schemas.data_chunk import DataChunk
from models.db_schemas.asset import Asset
from .schemas.data import ProcessRequest
import logging
from bson.objectid import ObjectId
from helpers import get_current_user_id


logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"],
)

@data_router.post("/upload/{project_id}")
async def upload_data(request:Request,project_id: str, file: UploadFile,
                       app_settings: Settings = Depends(get_settings),user_id: ObjectId = Depends(get_current_user_id)):
  
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id,user_id=user_id)
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
    
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    asset_res = Asset(
        asset_name=file_id,
        asset_type=AssetEnum.ASSET_TYPE_FILE.value,
        asset_size=os.path.getsize(file_path),
        asset_project_id=ObjectId(project.id),
    )

    asset_record = await asset_model.create_asset(asset_res)

    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "file_id": str(asset_record.id),
            }
        )
@data_router.post("/process/{project_id}")
async def process_data(request:Request,project_id: str, process_request: ProcessRequest,
                       app_settings: Settings = Depends(get_settings),user_id: ObjectId = Depends(get_current_user_id)):
    
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    reset = process_request.reset

    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_project_or_create_one(project_id=project_id,user_id=user_id)

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    project_files_ids = {}

    # If a file_id is present in the process_request, 
    # it retrieves that specific asset (file) from the database.
    if  process_request.file_id: 
        asset = await asset_model.get_asset_by_name_and_project_id(
            asset_name=process_request.file_id,
            project_id=project.id
        )
        project_files_ids = { asset.id : process_request.file_id }
    else:
        # If file_id is not provided,
        #  it retrieves all files (AssetEnum.ASSET_TYPE_FILE) linked to the project_id.
      
        all_assets = await asset_model.get_all_assets_by_project_id(
            project_id=project.id,
            asset_type=AssetEnum.ASSET_TYPE_FILE.value
            )
        project_files_ids = {asset.id : asset.asset_name for asset in all_assets }

    if len(project_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponeseEnum.NO_FILE_TO_PROCESS.value,
            }
        )
    process_controller = ProcessController(project_id=project_id)

    if reset:
        _  = await chunk_model.delete_chunks_by_projectId(project_id=project.id)

    chunks_len = 0
    proccessed_files = 0

    for asset_id ,file_id in project_files_ids.items():
        file_content = process_controller.get_fileContent(file_id)

        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

        file_chunks = process_controller.process_file_content(file_content=file_content,
                                                            chunk_size=chunk_size,overlap_size=overlap_size)


        if  file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": ResponeseEnum.FILE_PROCESS_FAILED.value,
                }
            )

        file_chunks_record = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=index + 1,
                chunk_project_id = project.id,
                chunk_asset_id = asset_id
            )
            for index, chunk in enumerate(file_chunks)
        ]
   
        chunks_len += await chunk_model.insert_many_chunks(chunks=file_chunks_record)
        proccessed_files += 1


    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "no_of_chunks": chunks_len,
            "no_of_files_processed": proccessed_files
        }
    )   
