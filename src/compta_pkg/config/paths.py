from pathlib import Path

class DataPath:
    base_path = Path(__file__).resolve().parents[5]
    compta_path = base_path / "Database" / "compta"
    excel_path = compta_path / "legacy" / "REVOLUT AVRIL 2025.xlsx"
    sqlite_dev_path = compta_path / "dev_database.db"
    table_name = "transactions"

if __name__ == "__main__":
    print("Configuration paths:")
    print(f"Base path: {DataPath.base_path}")
    print(f"Excel path: {DataPath.excel_path}")
    print(f"SQLite development path: {DataPath.sqlite_dev_path}")
    print(f"Table name: {DataPath.table_name}")