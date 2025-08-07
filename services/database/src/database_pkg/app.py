import shutil
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

from database_pkg.utils import get_db_connection, get_extension
from database_pkg.config.settings import database_settings
from database_pkg.config.schemas import SQLQuery, OwnerEnum, BankEnum, ExtensionEnum


app = FastAPI()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post(
    "/upload_file",
    summary="Upload a bank statement file",
    description="""
    Upload a bank statement file (PDF, CSV, XLSX, or XLS) for a given owner, year, month, and bank. 
    The file is saved in a structured directory based on year and month. 
    Allowed owners: G, N. Allowed banks: BNP, REVOLUT, HSBC, BNC.
    """,
)
async def upload_file(
    owner: OwnerEnum = Form(
        ..., description="Owner of the file. Allowed values: G, N.", examples=["G"]
    ),
    year: int = Form(..., description="Year of the statement.", examples=[2025]),
    month: int = Form(..., description="Month of the statement (1-12).", examples=[8]),
    bank: BankEnum = Form(
        ...,
        description="Bank name. Allowed values: BNP, REVOLUT, HSBC, BNC.",
        examples=["BNP"],
    ),
    file: UploadFile = File(
        ...,
        description="The statement file to upload. Allowed types: PDF, CSV, XLSX, XLS.",
    ),
    overwrite: bool = Form(
        False,
        description="If true, overwrite the file if it exists. If false, return 409 if file exists.",
        examples=[False],
    ),
):
    # Validate year and month
    if year < 1900 or year > 2100:
        raise HTTPException(
            status_code=400, detail="Invalid year. Must be between 1900 and 2100."
        )
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=400, detail="Invalid month. Must be between 1 and 12."
        )

    ext = get_extension(file.filename)
    try:
        ext_enum = ExtensionEnum(ext)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF, CSV, and Excel files are accepted.",
        )
    save_dir = Path(database_settings.blob_path) / "raw" / str(year) / str(month)
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / f"{owner.value}_{bank.value}.{ext}"
    if not overwrite and save_path.exists():
        raise HTTPException(
            status_code=409,
            detail="File already exists. Set overwrite=True to replace it.",
        )
    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"detail": "File uploaded successfully.", "path": str(save_path)}


@app.post(
    "/execute_sql",
    summary="Execute a SQL query",
    description="""
    Execute a raw SQL query against the database. For SELECT queries, returns the result rows as a list of dicts. For other queries, returns the number of affected rows.
    """,
)
async def execute_sql(
    sql_query: SQLQuery,
    conn=Depends(get_db_connection),
):
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query.query)
        if sql_query.query.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        else:
            conn.commit()
            result = {"rows_affected": cursor.rowcount}
        cursor.close()
        conn.close()
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.middleware("http")
async def catch_dependency_errors(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
