from ..db.collections.files import files_collection
from bson import ObjectId
import os
import base64
from pdf2image import convert_from_path
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(" OPENAI_API_KEY is not set in .env")

client = OpenAI(api_key=api_key)


def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")



async def process_file(id: str, file_path: str):
    # Update status → processing
    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "processing"}}
    )
    print(f"Processing file with id {id}")

   
    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": "Converting To Images"}}
    )

 
    pages = convert_from_path(file_path)
    images = []
    output_dir = f"/workspaces/Full RAG/uploads/images/{id}"
    os.makedirs(output_dir, exist_ok=True)

    for i, page in enumerate(pages, start=1):
        image_save_path = os.path.join(output_dir, f"image-{i}.jpg")
        page.save(image_save_path, "JPEG")
        images.append(image_save_path)

    
    images_base64 = [encode_image(img) for img in images]

    # Call OpenAI Vision model
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "What's in this image?"},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{images_base64[0]}",
                    },
                ],
            }
        ],
    )

    # Update status → success
    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "status": "Converting to images successful",
            "response": response.output_text
          }
         } )

    # Print response
    print("AI Response:", response.output_text)
    
# Email notification  queueing can be added here

# def process_file(file_id: str, file_path: str):
#     print(f"Processing file {file_id} at {file_path}", flush=True)
