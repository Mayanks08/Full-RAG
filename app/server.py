from fastapi import FastAPI, UploadFile, Path
from uuid import uuid4
from .utlis.file import save_to_disk
from .db.collections.files import files_collection, FilesSchema
from .queue.q import q
from .queue.worker import process_file
from bson import ObjectId



app = FastAPI()


@app.get("/")
def hello():
    return {"status": "Test mode"}

@app.get("/file/{id}")
async def get_file_by_id(id: str= Path(..., description="The ID of the file to retrieve")):
    db_file = await files_collection.find_one({"_id": ObjectId(id)})
    
    return{
      "id": str(db_file["_id"]),
      "name": db_file["name"],
      "status": db_file["status"],
      "response": db_file["response"] if "response" in db_file else None,
    }
    

@app.post("/upload")
async def upload_file(
    file: UploadFile
):
    

    db_file = await files_collection.insert_one(
      document= FilesSchema(
          name=file.filename,
          status="Saying"
      )
    )
    
    file_path = f"/workspaces/Full RAG/uploads/{str(db_file.inserted_id)}/{file.filename}"
    
    spath = await save_to_disk(file=await file.read(), path=file_path)
    
    q.enqueue(process_file, str(db_file.inserted_id), spath)
    
    await files_collection.update_one({"_id":db_file.inserted_id},{
        "$set": {
          "status": "queued"
            }
    })

    return {"file_id":str(db_file.inserted_id), "file_Path": spath}
