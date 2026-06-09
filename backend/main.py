from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import shutil
from parser import process_clash_matrix

app = FastAPI()

# Enable cross-origin resource sharing for flawless local network calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    temp_filename = "temp_uploaded_matrix.xlsx"
    
    # Save the incoming file stream locally to pass it to the parser
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Run your custom matrix processor script to extract the data array
        result_data = process_clash_matrix(temp_filename)
        
        # Stream the raw dictionary data array straight back to the browser window as JSON
        return {
            "status": "success",
            "data": result_data
        }
        
    except Exception as e:
        print(f"Parser Processing Engine Error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }