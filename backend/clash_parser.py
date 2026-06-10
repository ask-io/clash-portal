import openpyxl


def process_clash_matrix(file_path, selected_tiers=None):
    wb = openpyxl.load_workbook(file_path)
    ws = wb["Clash Detection Matrix"]

    if selected_tiers is None:
        selected_tiers = ['1', '2', '3', 'O']

    col_disciplines = {}
    row_disciplines = {}

    # Track horizontal discipline headers (Row 6, starting at Column 5)
    current_disp = None
    for c in range(5, ws.max_column + 1):
        val = ws.cell(row=6, column=c).value
        if val is not None and str(val).strip() != "":
            current_disp = str(val).strip()
        col_disciplines[c] = current_disp

    # Track vertical discipline headers (Column 2, starting at Row 9)
    current_row_disp = None
    for r in range(9, ws.max_row + 1):
        val = ws.cell(row=r, column=2).value
        if val is not None and str(val).strip() != "":
            current_row_disp = str(val).strip()
        row_disciplines[r] = current_row_disp

    # --- INDENTATION RESET: This list stays outside the header mapping loops! ---
    clash_records = []

    # Full rectangle scanner looking ONLY for numerical priorities
    for r in range(9, ws.max_row + 1):
        for c in range(5, ws.max_column + 1):
            cell_value = ws.cell(row=r, column=c).value

            # Skip empty spaces, 'X' alignment marks, AND 'O' operational marks ('O' operational marks are now strictly ignored, will be updated in the future if we want to reintroduce them as a separate category)
            if cell_value is None:
                continue

            val_cleaned = str(cell_value).strip().upper()
            if val_cleaned == 'X' or val_cleaned == 'O':
                continue

            # Extract the clean numerical string segment (handling decimals like '1.0')
            if "." in val_cleaned:
                val_str = val_cleaned.split(".")[0]
            else:
                val_str = val_cleaned

            # Double check that it's a true number before adding it
            if val_str in selected_tiers and val_str.isdigit():
                row_disp_out = col_disciplines.get(c)
                row_el_out = ws.cell(row=8, column=c).value

                col_disp_out = row_disciplines.get(r)
                col_el_out = ws.cell(row=r, column=4).value

                clash_records.append({
                    "Row Discipline": row_disp_out,
                    "Row Element": row_el_out,
                    "Column Discipline": col_disp_out,
                    "Column Element": col_el_out,
                    # Forced to a clean mathematical integer
                    "Priority": int(val_str)
                })

    # --- INDENTATION RESET: File export happens AFTER the scanning loops finish ---
    if "Clash_List" in wb.sheetnames:
        del wb["Clash_List"]

    ws_list = wb.create_sheet(title="Clash_List")

    # Fixed typo in Column Discipline header string
    headers = ["Row Discipline", "Row Element",
               "Column Discipline", "Column Element", "Priority"]
    ws_list.append(headers)

    # Loop through all found records and append them
    for rec in clash_records:
        ws_list.append([
            rec["Row Discipline"],
            rec["Row Element"],
            rec["Column Discipline"],
            rec["Column Element"],
            rec["Priority"]
        ])

# Adjust column widths for maximum readability
    ws_list.column_dimensions['A'].width = 22
    ws_list.column_dimensions['B'].width = 38
    ws_list.column_dimensions['C'].width = 22
    ws_list.column_dimensions['D'].width = 38
    ws_list.column_dimensions['E'].width = 12

    wb.save(file_path)
    return clash_records  # Returns the list of parsed dictionaries cleanly


# --- SAFE PRODUCTION RUNNER BLOCK ---
if __name__ == "__main__":
    # This will now ONLY run if you manually press "Run" on parser.py directly
    import os
    # Swapped to match your actual saved upload name
    test_file = "uploaded_matrix.xlsx"

    if os.path.exists(test_file):
        try:
            total_records = process_clash_matrix(test_file)
            print(
                f"Success! Processed the matrix and wrote {len(total_records)} rows.")
        except Exception as e:
            print(f"An execution error occurred: {e}")
    else:
        print(
            f"Local standalone test skipped: '{test_file}' not found. Ready for server deployment!")
