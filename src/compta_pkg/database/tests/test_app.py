from fastapi.testclient import TestClient

from compta_pkg.database.app import app
from compta_pkg.database.utils import get_db_connection


def test_execute_sql_select():
    class DummyCursor:
        def execute(self, query):
            assert query == "SELECT * FROM test"

        def fetchall(self):
            return [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]

        def close(self):
            pass

        @property
        def rowcount(self):
            return 2

    class DummyConn:
        def cursor(self):
            return DummyCursor()

        def commit(self):
            pass

        def close(self):
            pass

    def dummy_get_db_connection():
        return DummyConn()

    from compta_pkg.database import app as db_app

    db_app.app.dependency_overrides = {}
    db_app.app.dependency_overrides[get_db_connection] = dummy_get_db_connection
    test_client = TestClient(db_app.app)
    response = test_client.post("/execute_sql", json={"query": "SELECT * FROM test"})
    assert response.status_code == 200
    assert "result" in response.json()
    assert response.json()["result"] == [
        {"id": 1, "name": "foo"},
        {"id": 2, "name": "bar"},
    ]


def test_execute_sql_non_select():
    class DummyCursor:
        def execute(self, query):
            assert query == "UPDATE test SET value='baz' WHERE id=1"

        def close(self):
            pass

        @property
        def rowcount(self):
            return 1

    class DummyConn:
        def cursor(self):
            return DummyCursor()

        def commit(self):
            pass

        def close(self):
            pass

    def dummy_get_db_connection():
        return DummyConn()

    from compta_pkg.database import app as db_app

    db_app.app.dependency_overrides = {}
    db_app.app.dependency_overrides[get_db_connection] = dummy_get_db_connection
    test_client = TestClient(db_app.app)
    response = test_client.post(
        "/execute_sql", json={"query": "UPDATE test SET value='baz' WHERE id=1"}
    )
    assert response.status_code == 200
    assert response.json()["result"]["rows_affected"] == 1


def test_execute_sql_error():
    def dummy_get_db_connection():
        raise Exception("DB error")

    from compta_pkg.database import app as db_app

    db_app.app.dependency_overrides = {}
    db_app.app.dependency_overrides[get_db_connection] = dummy_get_db_connection
    test_client = TestClient(db_app.app)
    response = test_client.post("/execute_sql", json={"query": "SELECT * FROM test"})
    assert response.status_code == 400
    assert "DB error" in response.json()["detail"]
