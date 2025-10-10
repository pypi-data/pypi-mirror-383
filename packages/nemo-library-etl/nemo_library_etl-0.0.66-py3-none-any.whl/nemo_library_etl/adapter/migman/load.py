"""
MigMan ETL Load Module.

This module handles the loading phase of the MigMan ETL pipeline.
It takes the transformed data and loads it into the target system, typically the
Nemo database or data warehouse.

The loading process typically includes:
1. Data validation before insertion
2. Connection management to target systems
3. Batch processing for efficient data loading
4. Error handling and rollback capabilities
5. Data integrity checks post-loading
6. Performance optimization for large datasets
7. Comprehensive logging throughout the process

Classes:
    MigManLoad: Main class handling MigMan data loading.
"""

import logging
from typing import Union

import pandas as pd
from nemo_library_etl.adapter.migman.config_models import PipelineMigMan
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary

from nemo_library_etl.adapter.migman.enums import MigManTransformStep


class MigManLoad:
    """
    Handles loading of transformed MigMan data into target system.
    
    This class manages the loading phase of the MigMan ETL pipeline,
    providing methods to insert transformed data into the target system with
    proper error handling, validation, and performance optimization.
    
    The loader:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Manages database connections and transactions
    - Provides batch processing capabilities
    - Handles data validation before insertion
    - Ensures data integrity and consistency
    - Optimizes performance for large datasets
    
    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineMigMan): Pipeline configuration with loading settings.
    """
    
    def __init__(
        self, 
        nl: NemoLibrary, 
        cfg: PipelineMigMan, 
        logger: Union[logging.Logger, object], 
        fh: ETLFileHandler,
    ) -> None:
        """
        Initialize the MigMan Load instance.

        Sets up the loader with the necessary library instances, configuration,
        and logging capabilities for the loading process.

        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineMigMan): Pipeline configuration object containing
                                                          loading settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh

        super().__init__()           

    def load(self) -> None:
        """
        Execute the main loading process for MigMan data.
        
        This method orchestrates the complete loading process by:
        1. Connecting to the target system (database, data warehouse, etc.)
        2. Loading transformed data from the previous ETL phase
        3. Validating data before insertion
        4. Performing batch inserts for optimal performance
        5. Handling errors and implementing rollback mechanisms
        6. Verifying data integrity post-insertion
        7. Updating metadata and audit tables
        8. Cleaning up temporary resources
        
        The method provides detailed logging for monitoring and debugging purposes
        and ensures transaction safety through proper error handling.
        
        Note:
            The actual loading logic needs to be implemented based on
            the target system requirements and data models.
        """
        self.logger.info("Loading all MigMan objects")

        # load objects into Nemo
        
        # find the latest transform step that was run
        for table, model in self.cfg.extract.tables.items():
            if model.active is False:
                self.logger.info(f"Skipping inactive table: {table}")
                continue

            self.logger.info(f"Loading table {table}")
            
            data = None
            # find the latest transform step that was run
            for step in reversed(list(MigManTransformStep)):
                
                data = self.fh.readJSONL(
                    step=ETLStep.TRANSFORM,
                    entity=table,
                    substep=step,
                    ignore_nonexistent=True,
                )
                if data is not None and len(data) > 0:
                    self.logger.info(f"Found data for table {table} at step {step.value}, loading {len(data)} records")
                    break
                
            if data is None or len(data) == 0:
                self.logger.warning(f"No data found for table {table}, skipping load")
                continue
            
            data_df = pd.DataFrame(data)
            self.nl.ReUploadDataFrame(
                df=data_df,
                projectname=table,
                update_project_settings=False,
            )
            