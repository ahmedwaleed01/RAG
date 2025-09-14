from fastapi import FastAPI
from routes import base , data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import  get_settings
from .store.llm import LLMFactoryProvider

app = FastAPI()

@app.on_event("startup")
async def start_up_db():
    settings = get_settings()

    app.mongo_con = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_con[settings.MONGODB_DATABASE]

    llm_factory = LLMFactoryProvider(settings)

    app.generative_client = llm_factory.create(settings.EMBEDDING_BACKEND)
    app.generative_client.set_generation_model(settings.GENERATION_MODEL_ID)

    app.embedding_client = llm_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_MODEL_SIZE)

@app.on_event("shutdown")
async def shutdown_db():
    app.mongo_con.close()

    
app.include_router(base.base_router)
app.include_router(data.data_router)