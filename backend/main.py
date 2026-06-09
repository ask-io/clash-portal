# 1. Import FastAPI, file handling utilities, and your custom parsing engine
# 2. Initialize the FastAPI application instance
# 3. Create a POST network endpoint called "/upload" that accepts an incoming file stream
# 4. When a file arrives over the network:
#    - Read its contents into memory safely
#    - Save it down temporarily to your disk as "uploaded_matrix.xlsx"
#    - Pass that new file path straight into your process_clash_matrix() function
#    - Return a clean JSON success response showing how many records were parsed

from fastapi import FastAPI, UploadFile, File
import shutil
from parser import process_clash_matrix

app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to disk
        file_location = "uploaded_matrix.xlsx"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        records = process_clash_matrix(file_location)

        return {
            "status": "success",
            "message": f"Successfully processed {len(records)} clash records!",
            "record_count": len(records)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
