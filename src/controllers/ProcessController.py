from .BaseController import BaseController
from .ProjectController import ProjectController
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessEnum
import os


class ProcessController(BaseController):
    def __init__(self,project_id: str):
        super().__init__()
        self.project_dir = project_id
        self.project_path = ProjectController().get_projectPath(project_id)

    def get_fileExtension(self,file_id: str):
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self ,file_id: str):
        file_extension = self.get_fileExtension(file_id)
        file_path = os.path.join(self.project_path
                                 ,file_id)
        
        if os.path.exists(file_path) is False:
            return None

        if file_extension == ProcessEnum.TXT.value:
            return TextLoader(file_path, encoding='utf8')
        elif file_extension == ProcessEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        else:
            return None

    def get_fileContent(self,file_id: str):
        file_loader = self.get_file_loader(file_id)
        return file_loader.load() if file_loader else None

    def process_file_content(self,file_content:list,chunk_size: int=100,overlap_size: int=20):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_meta = [
            rec.metadata
            for rec in file_content
        ]

        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_meta
        )
        return chunks

    
  


    