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
Abstract interfaces for database plugins and adapters.
"""
from abc import ABC, abstractmethod
import contextlib
import logging
from typing import Any, Dict, List, Optional, Union
from ..documents import (
    BaseThothDbDocument,
    TableDocument,
    ColumnDocument,
    QueryDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument,
    ThothDbType
)
from ..helpers import (
    SSHConfig,
    SSHTunnel,
    extract_ssh_parameters,
    mask_sensitive_dict,
)


logger = logging.getLogger(__name__)


class DbAdapter(ABC):
    """
    Abstract adapter interface for database operations.
    Similar to ThothHaystackVectorStore adapter pattern.
    """
    
    def __init__(self, connection_params: Dict[str, Any]):
        """
        Initialize the database adapter.
        
        Args:
            connection_params: Database connection parameters
        """
        self.connection_params = connection_params
        self.connection = None
        self._initialized = False
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """
        Execute SQL query through adapter.
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch: How to fetch results ('all', 'one', or number)
            timeout: Query timeout in seconds
            
        Returns:
            Query results
        """
        pass
    
    @abstractmethod
    def get_tables_as_documents(self) -> List[TableDocument]:
        """Return tables as document objects"""
        pass
    
    @abstractmethod
    def get_columns_as_documents(self, table_name: str) -> List[ColumnDocument]:
        """Return columns as document objects"""
        pass
    
    @abstractmethod
    def get_foreign_keys_as_documents(self) -> List[ForeignKeyDocument]:
        """Return foreign keys as document objects"""
        pass
    
    @abstractmethod
    def get_schemas_as_documents(self) -> List[SchemaDocument]:
        """Return schemas as document objects"""
        pass
    
    @abstractmethod
    def get_indexes_as_documents(self, table_name: Optional[str] = None) -> List[IndexDocument]:
        """Return indexes as document objects"""
        pass
    
    @abstractmethod
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get unique values from the database.
        
        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary where:
                - outer key is table name
                - inner key is column name
                - value is list of unique values
        """
        pass
    
    @abstractmethod
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Get example data (most frequent values) for each column in a table.
        
        Args:
            table_name (str): The name of the table.
            number_of_rows (int, optional): Maximum number of example values to return per column. Defaults to 30.
            
        Returns:
            Dict[str, List[Any]]: A dictionary mapping column names to lists of example values.
        """
        pass
    
    def health_check(self) -> bool:
        """Check if database connection is healthy"""
        try:
            self.execute_query("SELECT 1", fetch="one")
            return True
        except Exception:
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information"""
        return {
            "adapter_type": self.__class__.__name__,
            "connection_params": {k: v for k, v in self.connection_params.items() if k != "password"},
            "connected": self.connection is not None,
            "healthy": self.health_check() if self.connection else False
        }


class DbPlugin(ABC):
    """
    Abstract plugin interface for database implementations.
    Each database type should implement this interface.
    """
    
    # Plugin metadata
    plugin_name: str = ""
    plugin_version: str = "1.0.0"
    supported_db_types: List[str] = []
    required_dependencies: List[str] = []
    
    def __init__(self, db_root_path: str, db_mode: str = "dev", **kwargs):
        """
        Initialize the database plugin.

        Args:
            db_root_path: Path to the database root directory
            db_mode: Database mode (dev, prod, etc.)
            **kwargs: Additional plugin-specific parameters
        """
        self.db_root_path = db_root_path
        self.db_mode = db_mode
        self.adapter: Optional[DbAdapter] = None
        self._initialized = False
        self._ssh_config: Optional[SSHConfig] = None
        self._ssh_tunnel: Optional[SSHTunnel] = None
        self._connection_params: Dict[str, Any] = {}

    @property
    def db_type(self) -> str:
        """
        Get the primary database type for this plugin.

        Returns:
            The first supported database type, or "unknown" if none specified
        """
        return self.supported_db_types[0] if self.supported_db_types else "unknown"
    
    @abstractmethod
    def create_adapter(self, **kwargs) -> DbAdapter:
        """Create and return a database adapter instance"""
        pass
    
    @abstractmethod
    def validate_connection_params(self, **kwargs) -> bool:
        """Validate connection parameters for this plugin"""
        pass
    
    def initialize(self, **kwargs) -> None:
        """Initialize the plugin with connection parameters"""
        connection_params = kwargs.copy()
        ssh_config, connection_params = extract_ssh_parameters(connection_params)
        self._ssh_config = ssh_config

        if ssh_config is not None:
            try:
                tunnel = SSHTunnel(ssh_config)
                local_host, local_port = tunnel.open()
                connection_params["host"] = local_host
                if local_port:
                    connection_params["port"] = local_port
                self._ssh_tunnel = tunnel
                logger.debug(
                    "SSH tunnel enabled for %s with params: %s",
                    self.plugin_name,
                    ssh_config.to_log_dict(),
                )
            except Exception as exc:  # pragma: no cover - runtime safeguard
                logger.error("Failed to open SSH tunnel for %s: %s", self.plugin_name, exc)
                raise

        if not self.validate_connection_params(**connection_params):
            if self._ssh_tunnel is not None:
                self._ssh_tunnel.close()
                self._ssh_tunnel = None
            raise ValueError(f"Invalid connection parameters for {self.plugin_name}")

        self.adapter = self.create_adapter(**connection_params)
        try:
            self.adapter.connect()
            self._initialized = True
            self._connection_params = mask_sensitive_dict(connection_params)
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        """Close database adapter and SSH tunnel if open."""

        if self.adapter is not None:
            with contextlib.suppress(Exception):
                self.adapter.disconnect()
            self.adapter = None

        if self._ssh_tunnel is not None:
            with contextlib.suppress(Exception):
                self._ssh_tunnel.close()
            self._ssh_tunnel = None

        self._initialized = False
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        info = {
            "name": self.plugin_name,
            "version": self.plugin_version,
            "supported_db_types": self.supported_db_types,
            "required_dependencies": self.required_dependencies,
            "initialized": self._initialized,
        }

        if self._connection_params:
            info["connection_params"] = self._connection_params

        if self._ssh_config is not None:
            info.update(
                {
                    "ssh_enabled": True,
                    "ssh_tunnel_active": bool(
                        self._ssh_tunnel and self._ssh_tunnel.is_active()
                    ),
                    "ssh_config": self._ssh_config.to_log_dict(),
                }
            )

        return info
    
    # Document-based operations
    def add_table_document(self, doc: TableDocument) -> str:
        """Add a table document (for metadata storage)"""
        return doc.id
    
    def add_column_document(self, doc: ColumnDocument) -> str:
        """Add a column document (for metadata storage)"""
        return doc.id
    
    def add_query_document(self, doc: QueryDocument) -> str:
        """Add a query document (for query history/templates)"""
        return doc.id
    
    def search_documents(self, query: str, doc_type: ThothDbType, top_k: int = 10) -> List[BaseThothDbDocument]:
        """Search for documents similar to query"""
        # Default implementation - can be overridden by plugins
        return []
    
    def get_document(self, doc_id: str) -> Optional[BaseThothDbDocument]:
        """Get document by ID"""
        # Default implementation - can be overridden by plugins
        return None
    
    def get_documents_by_type(self, doc_type: ThothDbType) -> List[BaseThothDbDocument]:
        """Get all documents of a specific type"""
        # Default implementation - can be overridden by plugins
        return []
    
    # Backward compatibility methods - delegate to adapter
    def execute_sql(self, sql: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute SQL query (backward compatibility)"""
        if not self.adapter:
            raise RuntimeError("Plugin not initialized")
        return self.adapter.execute_query(sql, params, fetch, timeout)
    
    def get_tables(self) -> List[Dict[str, str]]:
        """Get tables in old format (backward compatibility)"""
        if not self.adapter:
            raise RuntimeError("Plugin not initialized")
        
        table_docs = self.adapter.get_tables_as_documents()
        return [
            {
                "name": doc.table_name,
                "comment": doc.comment
            }
            for doc in table_docs
        ]
    
    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get columns in old format (backward compatibility)"""
        if not self.adapter:
            raise RuntimeError("Plugin not initialized")
        
        column_docs = self.adapter.get_columns_as_documents(table_name)
        return [
            {
                "name": doc.column_name,
                "data_type": doc.data_type,
                "comment": doc.comment,
                "is_pk": doc.is_pk
            }
            for doc in column_docs
        ]
    
    def get_foreign_keys(self) -> List[Dict[str, str]]:
        """Get foreign keys in old format (backward compatibility)"""
        if not self.adapter:
            raise RuntimeError("Plugin not initialized")
        
        fk_docs = self.adapter.get_foreign_keys_as_documents()
        return [
            {
                "source_table_name": doc.source_table_name,
                "source_column_name": doc.source_column_name,
                "target_table_name": doc.target_table_name,
                "target_column_name": doc.target_column_name
            }
            for doc in fk_docs
        ]
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values (backward compatibility)"""
        if not self.adapter:
            raise RuntimeError("Plugin not initialized")
        return self.adapter.get_unique_values()

    def __enter__(self) -> "DbPlugin":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def __del__(self):  # pragma: no cover - best effort cleanup
        try:
            self.close()
        except Exception:
            pass
