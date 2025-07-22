from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database_pkg.utils import get_db_connection

app = FastAPI()


class SQLQuery(BaseModel):
    query: str


@app.post("/execute_sql")
async def execute_sql(sql_query: SQLQuery, conn=Depends(get_db_connection)):
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
