from .BaseController import BaseController
from models.db_schemas import Project,DataChunk
from store.llm.LLMEnums import DocumentType
from typing import List


class NLPController(BaseController):

    def __init__(self, generative_client, embedding_client, vectordb_client):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generative_client = generative_client

    def create_collection_name(self, project_id):
        return  f"collection_{project_id}".strip()

    def reset_vector_db_collection(self, project:Project):
        collection_name = self.create_collection_name(project_id= project.project_id)
        return self.vectordb_client.delete_collection(collection_name= collection_name)

    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id= project.project_id)
        return self.vectordb_client.get_collection_info(collection_name= collection_name)
    
    def index_into_vector_db(self, project:Project, chunks: List[DataChunk],chunk_ids: List[int], reset: bool = False):

        collection_name = self.create_collection_name(project_id= project.project_id)


        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        vectors =[
            self.embedding_client.embed_text(
                text = text,
                document_type = DocumentType.DOCUMENT.value)
            for text in texts
        ]
        

        _ = self.vectordb_client.create_collection(
            collection_name= collection_name ,
            embedding_size= self.embedding_client.embedding_size ,
            reset= reset ,
        )


        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadatas,
            vectors=vectors,
            record_ids=chunk_ids,
        )


        return True