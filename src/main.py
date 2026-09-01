from fastapi import FastAPI
from routes import base , data , nlp, auth
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import  get_settings
from store.llm import LLMFactoryProvider
from store.vectordb import VectorDBFactoryProvider
from contextlib import asynccontextmanager
from store.llm.templates.template_parser import TemplateParser


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    app.mongo_con = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_con[settings.MONGODB_DATABASE]

    llm_factory = LLMFactoryProvider(settings)
    vectordb_factory = VectorDBFactoryProvider(settings)

    app.generative_client = llm_factory.create(settings.GENERATION_BACKEND)
    app.generative_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)

    app.vectordb_client = vectordb_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.DEFAULT_LANGUAGE,
        default_language=settings.DEFAULT_LANGUAGE)

    yield

    app.mongo_con.close()
    app.vectordb_client.disconnect()



app = FastAPI(lifespan=lifespan)

    
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(auth.auth_router)