"""
MigMan ETL Transform Module.

This module handles the transformation phase of the MigMan ETL pipeline.
It processes the extracted data, applies business rules, data cleaning, and formatting
to prepare the data for loading into the target system.

The transformation process typically includes:
1. Data validation and quality checks
2. Data type conversions and formatting
3. Business rule application
4. Data enrichment and calculated fields
5. Data structure normalization
6. Comprehensive logging throughout the process

Classes:
    MigManTransform: Main class handling MigMan data transformation.
"""

from importlib import resources
import logging
from typing import Union
from nemo_library_etl.adapter._utils.db_handler import ETLDuckDBHandler
from nemo_library_etl.adapter.migman.config_models_migman import ConfigMigMan
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary

from nemo_library_etl.adapter.migman.enums import MigManTransformStep


class MigManTransform:
    """
    Handles transformation of extracted MigMan data.
    
    This class manages the transformation phase of the MigMan ETL pipeline,
    providing methods to process, clean, and format the extracted data for loading
    into the target system.
    
    The transformer:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Applies business rules and data validation
    - Handles data type conversions and formatting
    - Provides data enrichment and calculated fields
    - Ensures data quality and consistency
    
    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineMigMan): Pipeline configuration with transformation settings.
    """
    
    def __init__(
        self, 
        nl: NemoLibrary, 
        cfg: ConfigMigMan, 
        logger: Union[logging.Logger, object], 
        fh: ETLFileHandler,
        local_database: ETLDuckDBHandler,
    ) -> None:
        """
        Initialize the MigMan Transform instance.

        Sets up the transformer with the necessary library instances, configuration,
        and logging capabilities for the transformation process.

        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineMigMan): Pipeline configuration object containing
                                                          transformation settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh
        self.local_database = local_database

        super().__init__()           

    def transform(self) -> None:
        """
        Execute the main transformation process for MigMan data.
        
        This method orchestrates the complete transformation process by:
        1. Loading extracted data from the previous ETL phase
        2. Applying data validation and quality checks
        3. Performing data type conversions and formatting
        4. Applying business rules and logic
        5. Creating calculated fields and data enrichment
        6. Ensuring data consistency and integrity
        7. Preparing data for the loading phase
        
        The method provides detailed logging for monitoring and debugging purposes
        and handles errors gracefully to ensure pipeline stability.
        
        Note:
            The actual transformation logic needs to be implemented based on
            the specific MigMan system requirements and business rules.
        """
        self.logger.info("Transforming all MigMan objects")

        # transform objects
        
        # start with joins. After this step, we have all data in our data modell
        self.joins()
        

    def joins(self) -> None:
        """
        Execute join operations for MigMan data transformation.
        
        This method handles the joining of data from different sources or tables
        as part of the transformation process. It ensures that related data is
        combined correctly based on specified keys and relationships.
        
        The join process includes:
        1. Identifying the datasets to be joined
        2. Defining the join keys and types (e.g., inner, left, right, full)
        3. Performing the join operation using efficient algorithms
        4. Validating the joined data for consistency and integrity
        5. Logging the join process for monitoring and debugging
        
        Note:
            The actual join logic needs to be implemented based on
            the specific MigMan system requirements and data relationships.
        """
        self.logger.info("Joining MigMan objects")

        # join objects
        if self.cfg.transform.join is None:
            return
        
        adapter = self.cfg.transform.join.adapter
        self.logger.info(f"Using adapter: {adapter}")
        
        for join_name, join_cfg in self.cfg.transform.join.joins.items():
            if not join_cfg.active:
                self.logger.info(f"Skipping inactive join: {join_name}")
                continue

            self.logger.info(f"Processing join: {join_name}")

            # load the JOIN SQL from the config
            file = (
                resources.files("nemo_library_etl")
                / "adapter"
                / "migman"
                / "config"
                / "joins"
                / adapter
                / join_cfg.file
            )
            with resources.as_file(file) as sql_file:
                query = sql_file.read_text(encoding="utf-8")

            if not query:
                raise ValueError(f"Join SQL file is empty: {join_cfg.file}")

            # add result_creation to the query
            table_name = MigManTransformStep.JOINS.value + "_" + join_name
            query = f"CREATE OR REPLACE TABLE \"{table_name}\" AS\n" + query

            # Execute the join query
            self.local_database.query(query)

            # export results from database 
            self.local_database.export_table(
                table_name=table_name,
                fh=self.fh,
                step=ETLStep.TRANSFORM,
                substep=MigManTransformStep.JOINS,
                entity=join_name,
                gzip_enabled=False,)

