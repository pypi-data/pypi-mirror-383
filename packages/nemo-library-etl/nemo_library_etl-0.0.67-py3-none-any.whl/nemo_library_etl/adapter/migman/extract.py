"""
MigMan ETL Extract Module.

This module handles the extraction phase of the MigMan ETL pipeline.
It provides functionality to extract data from MigMan systems and 
prepare it for the transformation phase.

The extraction process:
1. Connects to the MigMan system using configured credentials
2. Iterates through configured tables and extracts data
3. Handles inactive tables by skipping them
4. Uses ETLFileHandler for data persistence
5. Provides comprehensive logging throughout the process

Classes:
    MigManExtract: Main class handling MigMan data extraction.
"""

import logging
from typing import Union
from nemo_library_etl.adapter._utils.db_handler import ETLDuckDBHandler
from nemo_library_etl.adapter._utils.generic_odbc import GenericODBCExtract
from nemo_library_etl.adapter.migman.config_models_migman import ConfigMigMan
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary


class MigManExtract:
    """
    Handles extraction of data from MigMan system.
    
    This class manages the extraction phase of the MigMan ETL pipeline,
    providing methods to connect to MigMan systems, retrieve data,
    and prepare it for subsequent transformation and loading phases.
    
    The extractor:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Processes tables based on configuration settings
    - Handles both active and inactive table configurations
    - Leverages ETLFileHandler for data persistence
    
    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineMigMan): Pipeline configuration with extraction settings.
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
        Initialize the MigMan Extract instance.
        
        Sets up the extractor with the necessary library instances, configuration,
        and logging capabilities for the extraction process.
        
        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineZentis): Pipeline configuration object containing
                                                          extraction settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh
        self.local_database = local_database

        super().__init__()            
    
    def extract(self) -> None:
        """
        Execute the main extraction process for MigMan data.
        
        This method orchestrates the complete extraction process by:
        1. Logging the start of extraction
        2. Iterating through configured tables
        3. Skipping inactive tables
        4. Processing active tables and extracting their data
        5. Using ETLFileHandler for data persistence
        
        The method respects table activation settings and provides detailed
        logging for monitoring and debugging purposes.
        
        Note:
            The actual data extraction logic needs to be implemented based on
            the specific MigMan system requirements.
        """
        self.logger.info("Extracting all MigMan objects")

        # extract objects
        
        if self.cfg.extract.inforcom and self.cfg.extract.inforcom.active:
            
            odbc = GenericODBCExtract(
                nl=self.nl,
                cfg=self.cfg,
                logger=self.logger,
                fh=self.fh,
                odbc_connstr=self.cfg.extract.inforcom.odbc_connstr,
                timeout=self.cfg.extract.inforcom.timeout,
            )
            
            if not self.cfg.extract.inforcom.tables:
                self.logger.warning("No tables configured for extraction in MigMan INFORCOM section")
            else:
                for table_name, table_cfg in self.cfg.extract.inforcom.tables.items():
                    if not table_cfg.active:
                        self.logger.info(f"Skipping inactive table {table_name}")
                        continue
                    self.logger.info(f"Extracting table {table_name} from MigMan Infor.COM")
                    odbc.generic_odbc_extract(
                        query=f"SELECT * FROM {self.cfg.extract.inforcom.table_prefix}{table_name}",
                        step=ETLStep.EXTRACT,
                        entity=table_name,
                        chunksize=self.cfg.extract.inforcom.chunk_size if table_cfg.big_data else None,
                        gzip_enabled=True,
                    )
