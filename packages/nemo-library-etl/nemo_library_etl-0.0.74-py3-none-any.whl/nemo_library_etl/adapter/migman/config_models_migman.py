from typing import Dict, Optional
from pydantic import BaseModel, Field, conint

##############################################################
# Extract
##############################################################


class ExtractInforcomTableConfig(BaseModel):
    """Configuration for a single INFOR table."""

    description: str = ""
    big_data: bool = False
    active: bool = True

    class Config:
        extra = "forbid"  # avoid typos inside table items


class ExtractInforcomConfig(BaseModel):
    """ODBC-based extraction from INFORCOM (INFOR.* tables)."""

    active: bool = True
    odbc_connstr: str = Field(..., description="ODBC connection string for SQL Server")
    chunk_size: conint(gt=0) = 10_000
    timeout: conint(gt=0) = 300
    table_prefix: str = "INFOR."
    tables: Dict[str, ExtractInforcomTableConfig] = Field(
        default_factory=dict, description="Mapping from table name to its configuration"
    )

    class Config:
        extra = "forbid"  # keep schema tight for the inforcom block


class ExtractConfigMigMan(BaseModel):
    extract_active: bool = True
    inforcom: Optional[ExtractInforcomConfig] = None

    class Config:
        extra = "allow"  # allow future adapter-specific keys


##############################################################
# Transform
##############################################################


class TransformJoinsConfig(BaseModel):
    active: bool = True
    file: str


class TransformJoinConfig(BaseModel):
    adapter: str
    joins: Dict[str, TransformJoinsConfig] = Field(
        default_factory=dict,
        description="Mapping from adapter name to its join configuration",
    )


class TransformConfigMigMan(BaseModel):
    transform_active: bool = True
    join: Optional[TransformJoinConfig] = None


##############################################################
# Load
##############################################################


class LoadConfigMigMan(BaseModel):
    load_active: bool = True


##############################################################
# Full Config
##############################################################
class ConfigMigMan(BaseModel):

    config_version: str = "0.0.1"
    etl_directory: str = "./etl/migman"
    local_database: str = "./etl/migman/migman_etl.duckdb"
    extract: ExtractConfigMigMan = Field(default_factory=ExtractConfigMigMan)
    transform: TransformConfigMigMan = Field(default_factory=TransformConfigMigMan)
    load: LoadConfigMigMan = Field(default_factory=LoadConfigMigMan)

    class Config:
        extra = "allow"  # allow adapter-specific keys without failing


CONFIG_MODEL = ConfigMigMan
