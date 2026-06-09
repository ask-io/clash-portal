from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
from typing import List
from parser import process_clash_matrix
import openpyxl

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    # The default parameters now care strictly about numbers
    tiers: List[str] = Query(default=['1', '2', '3'])
):
    try:
        temp_file_path = "uploaded_matrix.xlsx"
        
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Clean inputs and ensure no 'O' slips through the parameters
        cleaned_tiers = [t.strip() for t in tiers if t.strip() in ['1', '2', '3']]
        if not cleaned_tiers:
            cleaned_tiers = ['1', '2', '3']
            
        # 1. Run our newly updated rectangle parser engine
        records = process_clash_matrix(temp_file_path, selected_tiers=cleaned_tiers)
        
        # 2. Pure numerical mathematical sorting (1 -> 2 -> 3)
        sorted_records = sorted(records, key=lambda x: x["Priority"])
        
        # 3. Write sorted records back to the Excel tracking tab
        wb = openpyxl.load_workbook(temp_file_path)
        ws_list = wb["Clash_List"]
        
        while ws_list.max_row > 1:
            ws_list.delete_rows(2)
            
        for rec in sorted_records:
            ws_list.append([
                rec["Row Discipline"],
                rec["Row Element"],
                rec["Column Discipline"],
                rec["Column Element"],
                rec["Priority"]
            ])
            
        wb.save(temp_file_path)
        
        return FileResponse(
            path=temp_file_path,
            filename="Priority_Clash_Report.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except Exception as e:
        return {"status": "error", "message": str(e)}