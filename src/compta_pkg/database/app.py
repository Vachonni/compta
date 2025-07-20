from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from compta_pkg.database.utils import get_db_connection

app = FastAPI()


class SQLQuery(BaseModel):
    query: str


@app.post("/execute_sql")
async def execute_sql(sql_query: SQLQuery):
    try:
        conn = get_db_connection()
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("compta_pkg.database.app:app", host="127.0.0.1", port=8000, reload=True)
