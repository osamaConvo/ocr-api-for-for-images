from logging import debug
from fastapi import FastAPI, UploadFile,File
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from text_extraction_images import text_extraction_images
from pydantic import BaseModel
from pdf2image import  convert_from_bytes,convert_from_path

import uvicorn
import os

app = FastAPI()

class ApiResponse(BaseModel):
    filename: str
    extract_text: list

@app.get("/")
async def home():
    return {"message": "Hello World"}


@app.post("/upload",response_model=ApiResponse)
async def uploadImage(file: UploadFile = File(...)):
    results = None
    if file.content_type == 'application/pdf':
        return JSONResponse(content=jsonable_encoder({'message':"Text extraction from pdf is not supported right now."}))
    
    elif file.content_type == 'image/jpeg' or file.content_type == 'image/png':
        contents = await file.read()
        results = text_extraction_images(contents)
        formatted_result = {
        'filename':file.filename,
        'extracted_text': results
        }
        return JSONResponse(content=jsonable_encoder(formatted_result))
    
    else:
        return JSONResponse(content=jsonable_encoder({'message':"File Format Not Supported"}))

if __name__ == "__main__":
    uvicorn.run('api:app',port=int(os.environ.get("PORT",8000)),log_level="info",debug=True)