import io
import tempfile
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

from database_pkg.app import app
from database_pkg.utils import get_db_connection


def test_healthz():
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


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

    app.dependency_overrides = {}
    app.dependency_overrides[get_db_connection] = dummy_get_db_connection
    test_client = TestClient(app)
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

    app.dependency_overrides = {}
    app.dependency_overrides[get_db_connection] = dummy_get_db_connection
    test_client = TestClient(app)
    response = test_client.post(
        "/execute_sql", json={"query": "UPDATE test SET value='baz' WHERE id=1"}
    )
    assert response.status_code == 200
    assert response.json()["result"]["rows_affected"] == 1


def test_execute_sql_error():
    def dummy_get_db_connection():
        raise Exception("DB error")

    app.dependency_overrides = {}
    app.dependency_overrides[get_db_connection] = dummy_get_db_connection
    test_client = TestClient(app)
    response = test_client.post("/execute_sql", json={"query": "SELECT * FROM test"})
    assert response.status_code == 400
    assert "DB error" in response.json()["detail"]


class TestUploadFile:
    """Test cases for the /upload_file endpoint."""

    def setup_method(self):
        """Set up test client and clear dependency overrides."""
        app.dependency_overrides = {}
        self.client = TestClient(app)

    def test_upload_file_success_pdf(self):
        """Test successful PDF file upload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("database_pkg.app.database_settings") as mock_settings:
                mock_settings.blob_path = temp_dir

                # Create a dummy PDF file
                pdf_content = b"%PDF-1.4 fake pdf content"
                files = {
                    "file": (
                        "test_statement.pdf",
                        io.BytesIO(pdf_content),
                        "application/pdf",
                    )
                }
                data = {
                    "owner": "G",
                    "year": 2025,
                    "month": 8,
                    "bank": "BNP",
                    "overwrite": False,
                }

                response = self.client.post("/upload_file", files=files, data=data)

                assert response.status_code == 200
                result = response.json()
                assert result["detail"] == "File uploaded successfully."
                # The actual file path should contain the enum values
                assert (
                    "G" in result["path"]
                    and "BNP" in result["path"]
                    and ".pdf" in result["path"]
                )

                # Check that file exists in the expected directory structure
                blob_dir = Path(temp_dir) / "raw" / "2025" / "8"
                assert blob_dir.exists()
                # Check that some .pdf file was created in the directory
                pdf_files = [f for f in blob_dir.iterdir() if f.suffix == ".pdf"]
                assert len(pdf_files) == 1

    def test_upload_file_success_csv(self):
        """Test successful CSV file upload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("database_pkg.app.database_settings") as mock_settings:
                mock_settings.blob_path = temp_dir

                csv_content = (
                    b"Date,Description,Amount\n2025-08-01,Test transaction,100.50"
                )
                files = {
                    "file": ("test_statement.csv", io.BytesIO(csv_content), "text/csv")
                }
                data = {
                    "owner": "N",
                    "year": 2025,
                    "month": 12,
                    "bank": "Revolut",  # Fix: Use "Revolut" not "REVOLUT" to match the enum
                    "overwrite": False,
                }

                response = self.client.post("/upload_file", files=files, data=data)

                assert response.status_code == 200
                result = response.json()
                assert result["detail"] == "File uploaded successfully."
                assert (
                    "N" in result["path"]
                    and "Revolut" in result["path"]
                    and ".csv" in result["path"]
                )

    def test_upload_file_success_xlsx(self):
        """Test successful Excel file upload."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("database_pkg.app.database_settings") as mock_settings:
                mock_settings.blob_path = temp_dir

                # Minimal Excel file content (just a header)
                excel_content = b"PK\x03\x04fake excel content"
                files = {
                    "file": (
                        "test_statement.xlsx",
                        io.BytesIO(excel_content),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                }
                data = {
                    "owner": "G",
                    "year": 2024,
                    "month": 1,
                    "bank": "HSBC",
                    "overwrite": False,
                }

                response = self.client.post("/upload_file", files=files, data=data)

                assert response.status_code == 200
                result = response.json()
                assert result["detail"] == "File uploaded successfully."
                assert (
                    "G" in result["path"]
                    and "HSBC" in result["path"]
                    and ".xlsx" in result["path"]
                )

    def test_upload_file_invalid_year_too_low(self):
        """Test upload with invalid year (too low)."""
        files = {"file": ("test.pdf", io.BytesIO(b"fake content"), "application/pdf")}
        data = {
            "owner": "G",
            "year": 1899,
            "month": 8,
            "bank": "BNP",
            "overwrite": False,
        }

        response = self.client.post("/upload_file", files=files, data=data)

        assert response.status_code == 400
        assert (
            "Invalid year. Must be between 1900 and 2100." in response.json()["detail"]
        )

    def test_upload_file_invalid_year_too_high(self):
        """Test upload with invalid year (too high)."""
        files = {"file": ("test.pdf", io.BytesIO(b"fake content"), "application/pdf")}
        data = {
            "owner": "G",
            "year": 2101,
            "month": 8,
            "bank": "BNP",
            "overwrite": False,
        }

        response = self.client.post("/upload_file", files=files, data=data)

        assert response.status_code == 400
        assert (
            "Invalid year. Must be between 1900 and 2100." in response.json()["detail"]
        )

    def test_upload_file_invalid_month_too_low(self):
        """Test upload with invalid month (too low)."""
        files = {"file": ("test.pdf", io.BytesIO(b"fake content"), "application/pdf")}
        data = {
            "owner": "G",
            "year": 2025,
            "month": 0,
            "bank": "BNP",
            "overwrite": False,
        }

        response = self.client.post("/upload_file", files=files, data=data)

        assert response.status_code == 400
        assert "Invalid month. Must be between 1 and 12." in response.json()["detail"]

    def test_upload_file_invalid_month_too_high(self):
        """Test upload with invalid month (too high)."""
        files = {"file": ("test.pdf", io.BytesIO(b"fake content"), "application/pdf")}
        data = {
            "owner": "G",
            "year": 2025,
            "month": 13,
            "bank": "BNP",
            "overwrite": False,
        }

        response = self.client.post("/upload_file", files=files, data=data)

        assert response.status_code == 400
        assert "Invalid month. Must be between 1 and 12." in response.json()["detail"]

    def test_upload_file_invalid_extension(self):
        """Test upload with invalid file extension."""
        files = {"file": ("test.txt", io.BytesIO(b"text content"), "text/plain")}
        data = {
            "owner": "G",
            "year": 2025,
            "month": 8,
            "bank": "BNP",
            "overwrite": False,
        }

        response = self.client.post("/upload_file", files=files, data=data)

        assert response.status_code == 400
        assert (
            "Invalid file type. Only PDF, CSV, and Excel files are accepted."
            in response.json()["detail"]
        )

    def test_upload_file_no_extension(self):
        """Test upload with file that has no extension."""
        files = {"file": ("test", io.BytesIO(b"content"), "application/octet-stream")}
        data = {
            "owner": "G",
            "year": 2025,
            "month": 8,
            "bank": "BNP",
            "overwrite": False,
        }

        response = self.client.post("/upload_file", files=files, data=data)

        assert response.status_code == 400
        assert (
            "Invalid file type. Only PDF, CSV, and Excel files are accepted."
            in response.json()["detail"]
        )

    def test_upload_file_exists_no_overwrite(self):
        """Test upload when file exists and overwrite is False."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("database_pkg.app.database_settings") as mock_settings:
                mock_settings.blob_path = temp_dir

                # Create the directory and file first
                save_dir = Path(temp_dir) / "raw" / "2025" / "8"
                save_dir.mkdir(parents=True, exist_ok=True)
                existing_file = save_dir / "G_BNP.pdf"
                existing_file.write_text("existing content")

                files = {
                    "file": ("test.pdf", io.BytesIO(b"new content"), "application/pdf")
                }
                data = {
                    "owner": "G",
                    "year": 2025,
                    "month": 8,
                    "bank": "BNP",
                    "overwrite": False,
                }

                response = self.client.post("/upload_file", files=files, data=data)

                assert response.status_code == 409
                assert (
                    "File already exists. Set overwrite=True to replace it."
                    in response.json()["detail"]
                )

    def test_upload_file_exists_with_overwrite(self):
        """Test upload when file exists and overwrite is True."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("database_pkg.app.database_settings") as mock_settings:
                mock_settings.blob_path = temp_dir

                # Create the directory and file first
                save_dir = Path(temp_dir) / "raw" / "2025" / "8"
                save_dir.mkdir(parents=True, exist_ok=True)
                existing_file = save_dir / "G_BNP.pdf"
                existing_file.write_text("existing content")

                new_content = b"new content"
                files = {
                    "file": ("test.pdf", io.BytesIO(new_content), "application/pdf")
                }
                data = {
                    "owner": "G",
                    "year": 2025,
                    "month": 8,
                    "bank": "BNP",
                    "overwrite": True,
                }

                response = self.client.post("/upload_file", files=files, data=data)

                assert response.status_code == 200
                result = response.json()
                assert result["detail"] == "File uploaded successfully."

                # Verify file was overwritten
                assert existing_file.read_bytes() == new_content

    def test_upload_file_invalid_owner(self):
        """Test upload with invalid owner value."""
        files = {"file": ("test.pdf", io.BytesIO(b"fake content"), "application/pdf")}
        data = {
            "owner": "X",  # Invalid owner
            "year": 2025,
            "month": 8,
            "bank": "BNP",
            "overwrite": False,
        }

        response = self.client.post("/upload_file", files=files, data=data)

        assert response.status_code == 422  # Validation error

    def test_upload_file_invalid_bank(self):
        """Test upload with invalid bank value."""
        files = {"file": ("test.pdf", io.BytesIO(b"fake content"), "application/pdf")}
        data = {
            "owner": "G",
            "year": 2025,
            "month": 8,
            "bank": "INVALID_BANK",  # Invalid bank
            "overwrite": False,
        }

        response = self.client.post("/upload_file", files=files, data=data)

        assert response.status_code == 422  # Validation error

    def test_upload_file_creates_directories(self):
        """Test that upload creates necessary directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("database_pkg.app.database_settings") as mock_settings:
                mock_settings.blob_path = temp_dir

                files = {
                    "file": ("test.pdf", io.BytesIO(b"content"), "application/pdf")
                }
                data = {
                    "owner": "N",
                    "year": 2023,
                    "month": 3,
                    "bank": "BNC",
                    "overwrite": False,
                }

                # Ensure directories don't exist initially
                expected_dir = Path(temp_dir) / "raw" / "2023" / "3"
                assert not expected_dir.exists()

                response = self.client.post("/upload_file", files=files, data=data)

                assert response.status_code == 200
                # Verify directories were created
                assert expected_dir.exists()
                assert (expected_dir / "N_BNC.pdf").exists()
