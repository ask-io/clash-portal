# BIM Clash Portal

A lightweight internal web tool for processing BIM clash detection matrices. Upload an Excel clash matrix, and the portal parses, categorises, and returns a structured priority report — ready to download in seconds.

**Live demo:** [clash-portal.onrender.com](https://clash-portal.onrender.com)

---

## What it does

The portal accepts a Navisworks-style clash detection matrix (`.xlsx`) and automatically:

- Scans the upper triangle of the matrix (rows 9–79, columns 5–75) to avoid duplicate mirrored entries
- Remaps legacy `O` values to the correct Optional tier internally, without modifying your source file
- Buckets every clash pair into one of five priority tiers
- Returns a formatted, colour-coded Excel report with one tab per tier

### Output tiers

| Sheet | Colour | Meaning |
|-------|--------|---------|
| Tier 1 | 🔴 Red | Critical |
| Tier 2 | 🟠 Orange | High |
| Tier 3 | 🟡 Yellow | Medium |
| Tier O | 🔵 Blue | Optional |
| Tier NA | 🟢 Green | Not Applicable / Empty |

Each sheet includes: Row Discipline, Row Element, Column Discipline, Column Element, and Priority.

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Backend | Python · FastAPI · Uvicorn |
| Excel processing | openpyxl |
| Frontend | Vanilla HTML · CSS · JavaScript |
| File upload | python-multipart |
| Hosting | Render |

---

## Project structure

```
├── main.py              # FastAPI app — upload endpoint, workbook assembly, streaming response
├── clash_parser.py      # Matrix scanning logic, tier bucketing, sheet writing
├── requirements.txt     # Python dependencies
└── frontend/
    ├── index.html       # UI markup
    ├── style.css        # Dark-theme styling with interactive blueprint canvas
    └── app.js           # File drag-and-drop, fetch, download trigger, status display
```

---

## Running locally

**Prerequisites:** Python 3.9+

```bash
# Clone the repo
git clone https://github.com/your-username/bim-clash-portal.git
cd bim-clash-portal

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## How to use

1. Open the portal in your browser
2. Drag and drop your clash detection matrix `.xlsx` file onto the upload zone, or click **Browse Files**
3. Click **Process & Download**
4. The portal processes the matrix and automatically downloads `Priority_Clash_Report.xlsx`
5. A summary of clash counts per tier is displayed on screen

---

## Input file format

The tool expects an Excel workbook with a sheet named **`Clash Detection Matrix`** structured as follows:

- **Row 6** — Column discipline headers (merged cells supported)
- **Row 8** — Column element names
- **Column 2** — Row discipline labels (merged cells supported)
- **Column 4** — Row element names
- **Rows 9–79, Columns 5–75** — Matrix data cells containing `1`, `2`, `3`, `O`, or blank

Values outside this range are ignored to avoid picking up legend rows or other sheet content.

---

## Dependencies

```
fastapi
uvicorn
openpyxl
python-multipart
```

---

## Deployment

The app is deployed on [Render](https://render.com) as a web service. To deploy your own instance:

1. Push the repo to GitHub
2. Create a new **Web Service** on Render, connected to your repo
3. Set the build command to `pip install -r requirements.txt`
4. Set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Author

Developed by **Abhijit Smiju Kunnel**
