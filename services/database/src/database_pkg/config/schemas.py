from enum import Enum
from pydantic import BaseModel, ConfigDict


# Enum for allowed APP_ENV values
class AppEnvEnum(str, Enum):
    DEV = "dev"
    LOCAL = "local"
    PROD = "prod"
    STAGING = "staging"


# Enum for allowed owners
class OwnerEnum(str, Enum):
    G = "G"
    N = "N"


# Enum for allowed banks
class BankEnum(str, Enum):
    BNP = "BNP"
    REVOLUT = "Revolut"
    HSBC = "HSBC"
    BNC = "BNC"


# Enum for allowed extensions
class ExtensionEnum(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"


# Pydantic schemas
class SQLQuery(BaseModel):
    query: str
    # For documentation purposes, provides example values
    model_config = ConfigDict(
        json_schema_extra={"example": {"query": "SELECT * FROM my_table"}}
    )
