# Copyright 2025 Marco Pancotti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
MariaDB plugin for Thoth SQL Database Manager.
Uses the MariaDB adapter from adapters.mariadb module.
"""

import logging
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from ..core.interfaces import DbPlugin, DbAdapter
from ..core.registry import register_plugin
from ..adapters.mariadb import MariaDBAdapter

logger = logging.getLogger(__name__)


@register_plugin("mariadb")
class MariaDBPlugin(DbPlugin):
    """MariaDB database plugin."""
    
    plugin_name = "MariaDB Plugin"
    plugin_version = "1.0.0"
    supported_db_types = ["mariadb"]
    required_dependencies = ["mariadb", "SQLAlchemy"]
    
    _instances = {}
    _lock = Lock()
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", **kwargs):
        super().__init__(db_root_path, db_mode, **kwargs)
        self.db_id = None
        self.db_directory_path = None
        self.host = None
        self.port = None
        self.dbname = None
        self.user = None
        self.password = None
        
        # LSH manager integration (for backward compatibility)
        self._lsh_manager = None
    
    @classmethod
    def get_instance(cls, host: str, port: int, dbname: str, user: str, password: str, 
                    db_root_path: str, db_mode: str = "dev", **kwargs):
        """Get or create a singleton instance based on connection parameters."""
        required_params = ['host', 'port', 'dbname', 'user', 'password', 'db_root_path']

        all_params = {
            'host': host,
            'port': port,
            'dbname': dbname,
            'user': user,
            'password': password,
            'db_root_path': db_root_path,
            'db_mode': db_mode,
            **kwargs
        }

        missing_params = [param for param in required_params if all_params.get(param) is None]
        if missing_params:
            raise ValueError(f"Missing required parameter{'s' if len(missing_params) > 1 else ''}: {', '.join(missing_params)}")

        with cls._lock:
            instance_key = (host, port, dbname, user, password, db_root_path, db_mode)
            
            if instance_key not in cls._instances:
                instance = cls(db_root_path=db_root_path, db_mode=db_mode, **all_params)
                instance.initialize(**all_params)
                cls._instances[instance_key] = instance
                
            return cls._instances[instance_key]
    
    def create_adapter(self, **kwargs) -> DbAdapter:
        """Create and return a MariaDB adapter instance."""
        # Map plugin parameters to adapter parameters
        connection_params = {
            'host': kwargs.get('host', 'localhost'),
            'port': kwargs.get('port', 3307),
            'database': kwargs.get('database') or kwargs.get('dbname'),
            'user': kwargs.get('user') or kwargs.get('username'),
            'password': kwargs.get('password')
        }
        return MariaDBAdapter(connection_params)
    
    def validate_connection_params(self, **kwargs) -> bool:
        """Validate connection parameters for MariaDB."""
        required = ['host', 'user', 'password']
        database = kwargs.get('database') or kwargs.get('dbname')
        
        if not database:
            logger.error("Either 'database' or 'dbname' is required for MariaDB")
            return False
        
        for param in required:
            if param not in kwargs:
                logger.error(f"Missing required parameter: {param}")
                return False
        
        port = kwargs.get('port', 3307)
        if not isinstance(port, int) or not (1 <= port <= 65535):
            logger.error("port must be an integer between 1 and 65535")
            return False
        
        return True
    
    def initialize(self, **kwargs) -> None:
        """Initialize the MariaDB plugin."""
        # Validate and extract parameters
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 3307)
        self.dbname = kwargs.get('database') or kwargs.get('dbname')
        self.user = kwargs.get('user') or kwargs.get('username')
        self.password = kwargs.get('password')
        
        # Set additional attributes
        for key, value in kwargs.items():
            if key not in ['host', 'port', 'database', 'dbname', 'user', 'username', 'password']:
                setattr(self, key, value)
        
        # Initialize with updated kwargs
        super().initialize(**kwargs)
        
        # Set up database directory path and ID
        self.db_id = self.dbname
        self._setup_directory_path(self.db_id)
        
        logger.info(f"MariaDB plugin initialized for database: {self.db_id} at {self.host}:{self.port}")
    
    def _setup_directory_path(self, db_id: str) -> None:
        """Set up the database directory path."""
        if isinstance(self.db_root_path, str):
            self.db_root_path = Path(self.db_root_path)
        
        self.db_directory_path = Path(self.db_root_path) / f"{self.db_mode}_databases" / db_id
        self.db_id = db_id
        
        # Reset LSH manager when directory path changes
        self._lsh_manager = None
    
    @property
    def lsh_manager(self):
        """Lazy load LSH manager for backward compatibility."""
        if self._lsh_manager is None and self.db_directory_path:
            from ..lsh.manager import LshManager
            self._lsh_manager = LshManager(self.db_directory_path)
        return self._lsh_manager
    
    # LSH integration methods for backward compatibility
    def set_lsh(self) -> str:
        """Set LSH for backward compatibility."""
        try:
            if self.lsh_manager and self.lsh_manager.load_lsh():
                return "success"
            else:
                return "error"
        except Exception as e:
            logger.error(f"Error loading LSH: {e}")
            return "error"
    
    def query_lsh(self, keyword: str, signature_size: int = 30, n_gram: int = 3, top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """Query LSH for backward compatibility."""
        if self.lsh_manager:
            try:
                return self.lsh_manager.query(
                    keyword=keyword,
                    signature_size=signature_size,
                    n_gram=n_gram,
                    top_n=top_n
                )
            except Exception as e:
                logger.error(f"LSH query failed: {e}")
                raise Exception(f"Error querying LSH for {self.db_id}: {e}")
        else:
            raise Exception(f"LSH not available for {self.db_id}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        base_info = super().get_plugin_info()
        
        if self.adapter:
            adapter_info = self.adapter.get_connection_info()
            base_info.update(adapter_info)
        
        base_info.update({
            "db_id": self.db_id,
            "host": self.host,
            "port": self.port,
            "database": self.dbname,
            "user": self.user,
            "db_directory_path": str(self.db_directory_path) if self.db_directory_path else None,
            "lsh_available": self.lsh_manager is not None
        })
        
        return base_info
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data through adapter."""
        if self.adapter:
            return self.adapter.get_example_data(table_name, number_of_rows)
        else:
            raise RuntimeError("Plugin not initialized")
    
    @classmethod
    def get_required_parameters(cls) -> List[str]:
        """Get list of required connection parameters."""
        return ['host', 'port', 'database', 'user', 'password']
    
    @classmethod
    def get_optional_parameters(cls) -> List[str]:
        """Get list of optional connection parameters."""
        return ['db_root_path', 'db_mode']