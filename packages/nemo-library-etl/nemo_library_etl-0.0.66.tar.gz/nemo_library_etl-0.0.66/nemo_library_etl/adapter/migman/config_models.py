"""
MigMan ETL Configuration Models.

This module defines Pydantic models for configuring the MigMan ETL pipeline.
These models provide type safety, validation, and structure for pipeline configuration,
including table-specific settings and overall pipeline control.

The models support:
- Table-level configuration with GUID tracking and activation flags
- Pipeline-wide configuration with phase control (extract/transform/load)
- Flexible configuration with additional fields support
- Version tracking for configuration compatibility
"""

from pathlib import Path
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class TableMigMan(BaseModel):
    """
    Configuration model for individual MigMan tables.
    
    This model defines the configuration structure for each table in the MigMan
    system that will be processed by the ETL pipeline. Each table configuration
    includes identification and control parameters.
    
    Attributes:
        GUID (str): Unique identifier for the table in the MigMan system.
        active (bool): Flag indicating whether this table should be processed.
                      Defaults to True.
    """
    active: bool = True

class SourceMigMan(BaseModel):
    """
    Configuration model for the source settings of MigMan ETL.
    
    This model encapsulates all configuration settings related to the data source
    from which MigMan data will be extracted.
    
    Attributes:
        type (str): Type of the data source (e.g., 'inforcom', 'database', etc.).
    """
    adapter_type: str
    adapter_config_json: Path
    duckdb_path: Path

class ExtractMigMan(BaseModel):
    """
    Configuration model for the extraction phase of MigMan ETL.
    
    This model encapsulates all configuration settings related to the data extraction
    phase, including which tables should be processed and their specific settings.
    
    Attributes:
        tables (Dict[str, TableMigMan]): Dictionary mapping table names 
                                                                to their configuration models.
                                                                Defaults to empty dict.
    """
    source: SourceMigMan = Field(default_factory=SourceMigMan)
    tables: Dict[str, TableMigMan] = Field(default_factory=dict)

class DuplicatesInforCOM(BaseModel):
    """
    Configuration model for handling duplicates in the transformation phase.

    This model defines the structure for specifying how duplicates should be
    identified and managed during the transformation phase of the ETL pipeline.

    Attributes:
        active (bool): Flag indicating whether duplicate handling is active.
                       Defaults to True.
        fields (List[str]): List of fields to consider when identifying duplicates.
                            Defaults to empty list.
    """

    active: bool = True
    primary_key: str
    fields: List[str] = Field(default_factory=list)
    
class TransformMigMan(BaseModel):
    """Configuration model for the transformation phase of MigMan ETL.

    Args:
        BaseModel (_type_): _description_
    """
    duplicates: Dict[str, DuplicatesInforCOM] = Field(default_factory=dict)
    
class PipelineMigMan(BaseModel):
    """
    Comprehensive configuration model for the entire MigMan ETL pipeline.
    
    This is the root configuration model that controls all aspects of the ETL pipeline,
    including version tracking, phase activation, and detailed configuration for each
    phase (extract, transform, load).
    
    The model supports:
    - Version tracking for configuration compatibility
    - Individual phase control (enable/disable extract, transform, load)
    - Structured configuration for each phase
    - Additional fields for future extensibility
    
    Attributes:
        config_version (str): Version identifier for configuration compatibility.
                            Defaults to "0.0.1".
        extract_active (bool): Whether the extraction phase should run. Defaults to True.
        transform_active (bool): Whether the transformation phase should run. Defaults to True.
        load_active (bool): Whether the loading phase should run. Defaults to True.
        extract (ExtractMigMan): Configuration for the extraction phase.
        transform (Dict[str, Any]): Configuration for the transformation phase.
                                  Defaults to empty dict.
        load (Dict[str, Any]): Configuration for the loading phase.
                             Defaults to empty dict.
    """
    config_version: str = "0.0.1"
    etl_directory: str = "./etl/migman"
    extract_active : bool = True
    transform_active : bool = True
    load_active : bool = True    
    extract: ExtractMigMan = Field(default_factory=ExtractMigMan)
    transform: TransformMigMan = Field(default_factory=TransformMigMan)
    load: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")


# Expose the adapter models for the loader:
# These constants provide easy access to the model classes for dynamic loading
# and configuration validation in the ETL pipeline infrastructure.
TABLE_MODEL = TableMigMan
PIPELINE_MODEL = PipelineMigMan
