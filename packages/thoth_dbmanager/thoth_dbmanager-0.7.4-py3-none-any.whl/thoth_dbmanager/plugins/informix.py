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
IBM Informix plugin implementation.
"""
import logging
from typing import Any, Dict, List
from pathlib import Path

from ..core.interfaces import DbPlugin, DbAdapter
from ..core.registry import register_plugin

# Import Informix SSH adapter (uses dbaccess via SSH - zero local dependencies)
from ..adapters.informix_ssh import InformixSSHAdapter

logger = logging.getLogger(__name__)


@register_plugin("informix")
class InformixPlugin(DbPlugin):
    """
    IBM Informix database plugin implementation.
    """
    
    plugin_name = "Informix Plugin"
    plugin_version = "1.0.0"
    supported_db_types = ["informix"]
    required_dependencies = ["paramiko"]
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", **kwargs):
        super().__init__(db_root_path, db_mode, **kwargs)
        self.db_id = None
        self.db_directory_path = None
        
        # LSH manager integration (for backward compatibility)
        self._lsh_manager = None
    
    def create_adapter(self, **kwargs) -> DbAdapter:
        """
        Create and return an Informix SSH adapter instance.
        
        Uses SSH + dbaccess approach (no native drivers required).
        
        Args:
            **kwargs: Connection parameters (SSH params already extracted by base class)
        
        Returns:
            InformixSSHAdapter instance
        """
        # Prepare connection parameters for adapter
        # SSH params have been extracted by base class into self._ssh_config
        # We need to merge them back for Informix which uses SSH directly
        adapter_params = kwargs.copy()
        
        # Always use _ssh_config if available (set by base class initialize())
        if self._ssh_config:
            # SSH params were extracted by base class, merge them back
            adapter_params['ssh_host'] = self._ssh_config.host
            adapter_params['ssh_port'] = self._ssh_config.port
            adapter_params['ssh_username'] = self._ssh_config.username
            adapter_params['ssh_password'] = self._ssh_config.password
            adapter_params['ssh_private_key_path'] = self._ssh_config.private_key_path
            adapter_params['ssh_private_key_passphrase'] = self._ssh_config.private_key_passphrase
            logger.debug("SSH config merged from base class _ssh_config")
        else:
            logger.warning("No _ssh_config available - SSH params may be missing!")
            logger.warning(f"Available params: {list(adapter_params.keys())}")
        
        logger.info("Creating Informix SSH adapter (zero native dependencies)")
        return InformixSSHAdapter(adapter_params)
    
    def validate_connection_params(self, **kwargs) -> bool:
        """
        Validate connection parameters for Informix SSH adapter.
        
        Required params:
        - database: Database name
        - SSH parameters (either in self._ssh_config or in kwargs)
        
        This method can be called in two ways:
        1. From base class initialize() - SSH params already extracted to self._ssh_config
        2. Directly for testing - SSH params should be in kwargs
        """
        # Database is required
        database = kwargs.get('database')
        if not database or not isinstance(database, str) or not database.strip():
            logger.error("Missing or invalid parameter: database")
            return False
        
        # Check for SSH configuration
        # First check if it's already set (called from initialize)
        if self._ssh_config:
            logger.debug(f"Validation passed: database={database}, ssh_config present")
            return True
        
        # Otherwise check kwargs for SSH parameters (direct validation call)
        # Check for at least ssh_enabled or ssh parameters
        has_ssh = any([
            kwargs.get('ssh_enabled'),
            kwargs.get('ssh_host'),
            # Also check for direct host/server which might be via tunnel
            (kwargs.get('host') and kwargs.get('server'))
        ])
        
        if not has_ssh:
            logger.error("SSH configuration is required for Informix SSH adapter")
            logger.error("Please provide: ssh_host, ssh_username, and ssh_key_file or ssh_password")
            return False
        
        logger.debug(f"Validation passed: database={database}, ssh params in kwargs")
        return True
    
    def initialize(self, **kwargs) -> None:
        """Initialize the Informix plugin"""
        super().initialize(**kwargs)
        
        # Set up database directory path (for LSH and other features)
        if 'database' in kwargs:
            self.db_id = kwargs['database']
            self._setup_directory_path(self.db_id)
        
        logger.info(f"Informix plugin initialized for database: {self.db_id}")
    
    def _setup_directory_path(self, db_id: str) -> None:
        """Set up the database directory path"""
        if isinstance(self.db_root_path, str):
            self.db_root_path = Path(self.db_root_path)
        
        self.db_directory_path = Path(self.db_root_path) / f"{self.db_mode}_databases" / db_id
        self.db_id = db_id
        
        # Reset LSH manager when directory path changes
        self._lsh_manager = None
    
    @property
    def lsh_manager(self):
        """Lazy load LSH manager for backward compatibility"""
        if self._lsh_manager is None and self.db_directory_path:
            from ..lsh.manager import LshManager
            self._lsh_manager = LshManager(self.db_directory_path)
        return self._lsh_manager
    
    # LSH integration methods for backward compatibility
    def set_lsh(self) -> str:
        """Set LSH for backward compatibility"""
        try:
            if self.lsh_manager and self.lsh_manager.load_lsh():
                return "success"
            else:
                return "error"
        except Exception as e:
            logger.error(f"Error loading LSH: {e}")
            return "error"
    
    def query_lsh(self, keyword: str, signature_size: int = 30, 
                  n_gram: int = 3, top_n: int = 10) -> Dict[str, Dict[str, List[str]]]:
        """Query LSH for backward compatibility"""
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
        """Get connection information with sensitive data masked"""
        base_info = super().get_plugin_info()
        
        if self.adapter:
            adapter_info = self.adapter.get_connection_info()
            # Mask sensitive data from adapter_info
            if 'connection_params' in adapter_info:
                adapter_info['connection_params'] = self._mask_sensitive_data(
                    adapter_info['connection_params']
                )
            base_info.update(adapter_info)
        
        base_info.update({
            "db_id": self.db_id,
            "db_directory_path": str(self.db_directory_path) if self.db_directory_path else None,
            "lsh_available": self.lsh_manager is not None
        })
        
        # Final pass to ensure no sensitive data in the entire dict
        base_info = self._mask_sensitive_data(base_info)
        
        return base_info
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """Recursively mask sensitive data in dictionaries"""
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                # Skip sensitive keys entirely (don't include them in output)
                if any(sensitive in key.lower() for sensitive in ['password', 'passphrase', 'secret']):
                    # Skip these keys entirely
                    continue
                elif 'key' in key.lower():
                    # For keys containing 'key', only keep file paths
                    if key.lower() in ['ssh_private_key_path', 'ssh_key_file', 'private_key_path']:
                        # Keep file paths
                        masked[key] = value
                    # Skip other key-related fields
                    continue
                else:
                    # Recursively process nested structures
                    masked[key] = self._mask_sensitive_data(value)
            return masked
        elif isinstance(data, (list, tuple)):
            return type(data)(self._mask_sensitive_data(item) for item in data)
        else:
            return data
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """Get example data through adapter"""
        if self.adapter:
            return self.adapter.get_example_data(table_name, number_of_rows)
        else:
            raise RuntimeError("Plugin not initialized")
