from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse as StaticFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import io
import openpyxl
from clash_parser import process_clash_matrix

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND = os.path.join(os.path.dirname(__file__), "frontend")


@app.get("/")
def serve_index():
    return StaticFile(os.path.join(FRONTEND, "index.html"))


@app.get("/app.js")
def serve_js():
    return StaticFile(os.path.join(FRONTEND, "app.js"), media_type="application/javascript")


@app.get("/style.css")
def serve_css():
    return StaticFile(os.path.join(FRONTEND, "style.css"), media_type="text/css")


OUTPUT_FILENAME = "Priority_Clash_Report.xlsx"


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    current_dir = os.path.dirname(__file__)
    temp_location = os.path.join(current_dir, "uploaded_matrix.xlsx")
    final_output_path = os.path.join(current_dir, OUTPUT_FILENAME)

    with open(temp_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        records = process_clash_matrix(temp_location)
        print(f"Parser returned {len(records)} records!")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Clash Priority Report"

        headers = ["Row Discipline", "Row Element",
                   "Column Discipline", "Column Element", "Priority"]
        ws.append(headers)

        for item in records:
            if isinstance(item, dict):
                ws.append([
                    item.get("Row Discipline", item.get("row_discipline", "")),
                    item.get("Row Element", item.get("row_element", "")),
                    item.get("Column Discipline", item.get(
                        "column_discipline", "")),
                    item.get("Column Element", item.get("column_element", "")),
                    item.get("Priority", item.get("priority", ""))
                ])

        ws.column_dimensions['A'].width = 22
        ws.column_dimensions['B'].width = 38
        ws.column_dimensions['C'].width = 22
        ws.column_dimensions['D'].width = 38
        ws.column_dimensions['E'].width = 12

        with open(final_output_path, "wb") as f:
            wb.save(f)

        with open(final_output_path, "rb") as f:
            file_bytes = f.read()

        print(f"Sending {len(file_bytes)} bytes to browser")

        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{OUTPUT_FILENAME}"',
                "Content-Length": str(len(file_bytes)),
                "Access-Control-Expose-Headers": "Content-Disposition, Content-Length",
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
