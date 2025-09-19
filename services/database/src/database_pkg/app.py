import shutil
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse

from fastapi_mcp import FastApiMCP

from database_pkg.utils import get_db_connection, get_extension
from database_pkg.config.settings import database_settings
from database_pkg.config.schemas import SQLQuery, OwnerEnum, BankEnum, ExtensionEnum


app = FastAPI()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.middleware("http")
async def catch_dependency_errors(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})


@app.post(
    "/execute_sql",
    summary="Execute a SQL query",
    description="""
    Execute a raw SQL query against the database. For SELECT queries, returns the result rows as a list of dicts. For other queries, returns the number of affected rows.
    CREATE TABLE "transactions" (
        "Type" TEXT,
        "Product" TEXT,
        "Started Date" TIMESTAMP,
        "Completed Date" TIMESTAMP,
        "Description" TEXT,
        "Amount" REAL,
        "Fee" REAL,
        "Currency" TEXT,
        "QUI" TEXT,
        "COMMENT" TEXT
    )
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


@app.get(
    "/extract_file",
    summary="Extract a file from the Database Blob",
    description="""
    Retrieve a file.

    The `path` parameter MUST be absolute and ONLY these two forms are accepted:
    1. The exact absolute path previously returned by /upload_file (i.e. any absolute path already inside the
       current configured blob root directory).
    2. An absolute path that starts with `/blob/...` (environment-agnostic). If the segment immediately after
       `/blob/` is `dev` or `prod` it is ignored.

    All other shapes (relative paths, absolute paths outside the blob root that do not start with `/blob/`) are rejected.
    """,
)
async def extract_file(path: str):
    blob_root = Path(database_settings.blob_path).resolve()
    p = Path(path)
    if not p.is_absolute():
        raise HTTPException(status_code=400, detail="Path must be absolute.")

    try:
        # Case 1: already within blob root
        rel = p.resolve().relative_to(blob_root)
        requested_path = blob_root / rel
    except Exception:
        # Case 2: starts with /blob/
        if p.parts[:2] == ("/", "blob"):
            after = list(p.parts[2:])
            if after and after[0] in {"dev", "prod"}:
                after = after[1:]
            requested_path = (blob_root / Path(*after)).resolve()
            if not str(requested_path).startswith(str(blob_root)):
                raise HTTPException(
                    status_code=400, detail="Resolved path escapes blob root."
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Path must either be inside the blob root or start with /blob/",
            )

    if not requested_path.exists() or not requested_path.is_file():
        raise HTTPException(
            status_code=404, detail=f"File not found at: {requested_path}"
        )

    ext = requested_path.suffix.lower().lstrip(".")
    media_types = {
        "pdf": "application/pdf",
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xls": "application/vnd.ms-excel",
    }
    media_type = media_types.get(ext, "application/octet-stream")
    return FileResponse(
        path=requested_path, media_type=media_type, filename=requested_path.name
    )


# Integrate MCP server
mcp = FastApiMCP(app)
mcp.mount_http()
