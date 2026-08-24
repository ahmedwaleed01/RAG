from typing import List
from fastapi import APIRouter, Depends , FastAPI, UploadFile , status,Request
from models import ProjectModel ,ChunkModel
from controllers import NLPController
from models.enums import ResponeseEnum
from fastapi.responses import JSONResponse
from helpers import get_settings, Settings
import logging
from bson.objectid import ObjectId
from .schemas import PushRequest , SearchRequest


logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request, project_id:str, push_request:PushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponeseEnum.PROJECT_NOT_FOUND.value
            }
        )
    
    nlp_controller = NLPController(
        embedding_client= request.app.embedding_client,
        generative_client= request.app.generative_client,
        vectordb_client= request.app.vectordb_client,
        template_parser= request.app.template_parser
    )

    chunk_model = await ChunkModel.create_instance(db_client= request.app.db_client)

    chunks_found = True
    page_number  = 1
    indx = 0

    while chunks_found:
        chunks_page = await chunk_model.get_project_chunks(project_id= project.id, page_number= page_number)
       
        if not chunks_page or len(chunks_page) == 0:
            chunks_found = False
            break
        
        page_number +=1

        chunk_ids = list(range(indx, indx + len(chunks_page)))
        indx += len(chunks_page)

        is_inserted = nlp_controller.index_into_vector_db(
            chunks= chunks_page,
            project= project,
            reset= push_request.reset == 1,
            chunk_ids = chunk_ids,
        )

        if not is_inserted :
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": ResponeseEnum.VECTOR_DB_ERROR.value
                }
            )
        
    return JSONResponse(
        content={
            "message" : ResponeseEnum.VECTOR_DB_SUCCESS.value
        }
    )

@nlp_router.get("/index/info/{project_id}")
async def get_index_info(request:Request, project_id:str):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponeseEnum.PROJECT_NOT_FOUND.value
            }
        )

    nlp_controller = NLPController(
        embedding_client= request.app.embedding_client,
        generative_client= request.app.generative_client,
        vectordb_client= request.app.vectordb_client,
        template_parser= request.app.template_parser
    )

    collection_info = nlp_controller.get_vector_db_collection_info( project=project )

    return JSONResponse(
        content={
          "collection_info" : collection_info.dict()
        }
    )

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id:str , search_request:SearchRequest ):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponeseEnum.PROJECT_NOT_FOUND.value
            }
        )
    
    
    nlp_controller = NLPController(
        embedding_client= request.app.embedding_client,
        generative_client= request.app.generative_client,
        vectordb_client= request.app.vectordb_client,
        template_parser= request.app.template_parser
    )
    
    search_result = nlp_controller.search_vector_db_collection(
        project= project,
        text = search_request.text,
        limit= search_request.limit
    )

    if not search_result:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponeseEnum.NO_SEARCH_VECTOR_DB.value
            }
        )
    
    return JSONResponse(
        content={
          "signal": ResponeseEnum.SEARCH_VECTOR_DB_SUCCESS.value,
          "results" : [ search_result_item.dict() for search_result_item in search_result]
        }
    )

@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id:str , search_request:SearchRequest ):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project :
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponeseEnum.PROJECT_NOT_FOUND.value
            }
        )
    
    
    nlp_controller = NLPController(
        embedding_client= request.app.embedding_client,
        generative_client= request.app.generative_client,
        vectordb_client= request.app.vectordb_client,
        template_parser= request.app.template_parser
    )

    answer, full_prompt, chat_history = nlp_controller.answer_rag_question(
        project= project,
        text = search_request.text,
        limit= search_request.limit
    )

    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponeseEnum.RAG_ANSWER_FAILED.value
            }
        )

    return JSONResponse(
        content={
          "signal": ResponeseEnum.RAG_ANSWER_SUCCESS.value,
          "answer" : answer,
          "full_prompt" : full_prompt,
          "chat_history" : chat_history
        }
    )