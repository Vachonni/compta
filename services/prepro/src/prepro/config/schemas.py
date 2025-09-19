"""Schemas for project prepro"""

from enum import Enum

class AppEnvEnum(str, Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"
