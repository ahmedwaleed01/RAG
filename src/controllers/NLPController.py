from .BaseController import BaseController
from models.db_schemas import Project,DataChunk
from store.llm.LLMEnums import DocumentType
from typing import List
import json


class NLPController(BaseController):

    def __init__(self, generative_client, embedding_client, vectordb_client,template_parser):
        super().__init__()
        self.vectordb_client = vectordb_client
        self.embedding_client = embedding_client
        self.generative_client = generative_client
        self.template_parser = template_parser

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

    def search_vector_db_collection(self, project: Project, text: str, limit : int = 5):

        # get collection name
        collection_name = self.create_collection_name(project_id= project.project_id)

        # get text embedding vector
        vector = self.embedding_client.embed_text(text= text, document_type = DocumentType.QUERY.value )

        if not vector or len(vector) == 0:
            return None
        
        results = self.vectordb_client.search_by_vector(collection_name= collection_name, vector= vector, limit = limit)

        if not results:
            return None

        return results

    def answer_rag_question(self, project: Project, text: str, limit : int = 5):

       answer , full_prompt , chat_history = None, None, None

       retreived_results = self.search_vector_db_collection(project= project, text= text, limit = limit)

       if not retreived_results or len(retreived_results) == 0:
            return None

       # generate answer using generative model
       system_prompt = self.template_parser.get(
            group="rag",
            key="system_prompt",
        )

       document_prompt = "\n".join([
            self.template_parser.get(
                group="rag",
                key="document_prompt",
                vars={
                    "doc_no": idx + 1,
                    "chunk_text": doc.text
                }
            )
            for idx,doc in enumerate(retreived_results)
        ])

       footer_prompt = self.template_parser.get(
            group="rag",
            key="footer_prompt",
        )

       chat_history = [
           self.generative_client.construct_prompt(
               prompt=system_prompt,
               role=self.generative_client.enums.SYSTEM.value,
           )
       ]

       full_prompt = "\n\n".join([
            document_prompt,
            footer_prompt
        ])

       answer = self.generative_client.generate_text(
           prompt=full_prompt,
           chat_history=chat_history
       )

       return answer , full_prompt , chat_history