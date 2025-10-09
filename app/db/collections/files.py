from typing import TypedDict, Optional
from pydantic import Field
from pymongo.asynchronous.collection import AsyncCollection
from ..db import database


class FilesSchema(TypedDict):
    name:str=Field(..., description="Name of the files")
    status: str = Field(...,description="status of the  files")
    path: str = Field(..., description="path of the files")
    response: Optional[str] = Field(None, description="response from the AI model")
    
COLLECTION_NAME = "files"
files_collection: AsyncCollection = database[COLLECTION_NAME]