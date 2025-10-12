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
MariaDB adapter implementation.
"""
import logging
from typing import Any, Dict, List, Optional, Union
import mariadb
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError

from ..core.interfaces import DbAdapter
from ..documents import (
    TableDocument,
    ColumnDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument
)

logger = logging.getLogger(__name__)


class MariaDBAdapter(DbAdapter):
    """
    MariaDB database adapter implementation.
    """
    
    def __init__(self, connection_params: Dict[str, Any]):
        super().__init__(connection_params)
        self.engine = None
        self.raw_connection = None
        self.host = connection_params.get('host', 'localhost')
        self.port = connection_params.get('port', 3307)
        self.database = connection_params.get('database')
        self.user = connection_params.get('user')
        self.password = connection_params.get('password')
    
    def connect(self) -> None:
        """Establish MariaDB connection"""
        try:
            # Create SQLAlchemy engine
            connection_string = self._build_connection_string()
            self.engine = create_engine(connection_string, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Also create raw mariadb connection for specific operations
            self.raw_connection = mariadb.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            
            self._initialized = True
            logger.info("MariaDB connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MariaDB: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close MariaDB connection"""
        try:
            if self.engine:
                self.engine.dispose()
                self.engine = None
            
            if self.raw_connection:
                self.raw_connection.close()
                self.raw_connection = None
            
            self._initialized = False
            logger.info("MariaDB connection closed")
            
        except Exception as e:
            logger.error(f"Error closing MariaDB connection: {e}")
    
    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string for MariaDB"""
        if not all([self.database, self.user, self.password]):
            raise ValueError("Missing required connection parameters: database, user, password")
        
        # MariaDB uses mysql+pymysql or mariadb+mariadbconnector dialect
        return f"mariadb+mariadbconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute SQL query"""
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            with self.engine.connect() as conn:
                # MariaDB doesn't have direct query timeout in the same way
                # but we can set connection timeout
                conn.execute(text(f"SET SESSION max_statement_time = {timeout}"))
                
                # Execute query
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # Handle different fetch modes
                if query.strip().upper().startswith(('SELECT', 'WITH', 'SHOW', 'DESCRIBE')):
                    if fetch == "all":
                        return [dict(row._mapping) for row in result]
                    elif fetch == "one":
                        row = result.first()
                        return dict(row._mapping) if row else None
                    elif isinstance(fetch, int):
                        rows = result.fetchmany(fetch)
                        return [dict(row._mapping) for row in rows]
                else:
                    # For INSERT, UPDATE, DELETE
                    conn.commit()
                    return result.rowcount
                    
        except SQLAlchemyError as e:
            logger.error(f"MariaDB query execution failed: {e}")
            raise
    
    def get_tables_as_documents(self) -> List[TableDocument]:
        """Return tables as document objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            inspector = inspect(self.engine)
            tables = []
            
            for table_name in inspector.get_table_names():
                # Get row count
                count_result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}", fetch="one")
                row_count = count_result.get('count', 0) if count_result else 0
                
                # Get column count
                columns = inspector.get_columns(table_name)
                
                # Get table comment (if available)
                table_comment = ""
                try:
                    comment_result = self.execute_query(
                        f"SELECT table_comment FROM information_schema.tables WHERE table_name = '{table_name}'",
                        fetch="one"
                    )
                    table_comment = comment_result.get('table_comment', '') if comment_result else ''
                except:
                    pass
                
                tables.append(TableDocument(
                    table_name=table_name,
                    table_type="TABLE",
                    row_count=row_count,
                    column_count=len(columns),
                    description=table_comment
                ))
            
            return tables
            
        except Exception as e:
            logger.error(f"Error getting tables as documents: {e}")
            raise
    
    def get_columns_as_documents(self, table_name: str) -> List[ColumnDocument]:
        """Return columns as document objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            inspector = inspect(self.engine)
            columns = []
            
            for col in inspector.get_columns(table_name):
                columns.append(ColumnDocument(
                    table_name=table_name,
                    column_name=col['name'],
                    data_type=str(col['type']),
                    is_nullable=col.get('nullable', True),
                    column_default=col.get('default'),
                    is_pk=col.get('primary_key', False),
                    column_comment=col.get('comment', '')
                ))
            
            # Mark primary keys
            pk_constraint = inspector.get_pk_constraint(table_name)
            if pk_constraint and pk_constraint.get('constrained_columns'):
                pk_columns = pk_constraint['constrained_columns']
                for col in columns:
                    if col.column_name in pk_columns:
                        col.is_pk = True
            
            return columns
            
        except Exception as e:
            logger.error(f"Error getting columns as documents: {e}")
            raise
    
    def get_foreign_keys_as_documents(self) -> List[ForeignKeyDocument]:
        """Return foreign keys as document objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            inspector = inspect(self.engine)
            foreign_keys = []
            
            for table_name in inspector.get_table_names():
                for fk in inspector.get_foreign_keys(table_name):
                    # Each foreign key can have multiple column pairs
                    for i, const_col in enumerate(fk['constrained_columns']):
                        foreign_keys.append(ForeignKeyDocument(
                            constraint_name=fk['name'],
                            table_name=table_name,
                            column_name=const_col,
                            foreign_table_name=fk['referred_table'],
                            foreign_column_name=fk['referred_columns'][i] if i < len(fk['referred_columns']) else None
                        ))
            
            return foreign_keys
            
        except Exception as e:
            logger.error(f"Error getting foreign keys as documents: {e}")
            raise
    
    def get_schemas_as_documents(self) -> List[SchemaDocument]:
        """Return schemas as document objects"""
        # MariaDB uses database as schema concept
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            # Get current database as schema
            result = self.execute_query("SELECT DATABASE() as db_name", fetch="one")
            current_db = result.get('db_name') if result else self.database
            
            # Get table count for current database
            tables = self.get_tables_as_documents()
            
            return [SchemaDocument(
                catalog_name=current_db,
                schema_name=current_db,
                schema_owner=self.user,
                table_count=len(tables)
            )]
            
        except Exception as e:
            logger.error(f"Error getting schemas as documents: {e}")
            raise
    
    def get_indexes_as_documents(self, table_name: Optional[str] = None) -> List[IndexDocument]:
        """Return indexes as document objects"""
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            inspector = inspect(self.engine)
            indexes = []
            
            # Get tables to process
            tables = [table_name] if table_name else inspector.get_table_names()
            
            for tbl in tables:
                for idx in inspector.get_indexes(tbl):
                    indexes.append(IndexDocument(
                        table_name=tbl,
                        index_name=idx['name'],
                        column_names=idx['column_names'],
                        is_unique=idx.get('unique', False),
                        index_type='BTREE'  # MariaDB default
                    ))
            
            return indexes
            
        except Exception as e:
            logger.error(f"Error getting indexes as documents: {e}")
            raise
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get unique values from the database.
        
        Returns:
            Dict[str, Dict[str, List[str]]]: Dictionary where:
                - outer key is table name
                - inner key is column name
                - value is list of unique values
        """
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            inspector = inspect(self.engine)
            unique_values = {}
            
            for table_name in inspector.get_table_names():
                unique_values[table_name] = {}
                
                for col in inspector.get_columns(table_name):
                    col_name = col['name']
                    # Only get unique values for reasonable data types
                    col_type = str(col['type']).upper()
                    
                    if any(t in col_type for t in ['VARCHAR', 'CHAR', 'TEXT', 'INT', 'ENUM']):
                        try:
                            query = f"SELECT DISTINCT `{col_name}` FROM `{table_name}` LIMIT 100"
                            result = self.execute_query(query)
                            
                            values = []
                            for row in result:
                                val = row.get(col_name)
                                if val is not None:
                                    values.append(str(val))
                            
                            if values:
                                unique_values[table_name][col_name] = values
                                
                        except Exception as e:
                            logger.debug(f"Could not get unique values for {table_name}.{col_name}: {e}")
                            continue
            
            return unique_values
            
        except Exception as e:
            logger.error(f"Error getting unique values: {e}")
            raise
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Get example data (most frequent values) for each column in a table.
        
        Args:
            table_name (str): The name of the table.
            number_of_rows (int, optional): Maximum number of example values to return per column. Defaults to 30.
            
        Returns:
            Dict[str, List[Any]]: A dictionary mapping column names to lists of example values.
        """
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            
            example_data = {}
            
            for col in columns:
                col_name = col['name']
                col_type = str(col['type']).upper()
                
                # Skip blob/binary columns
                if any(t in col_type for t in ['BLOB', 'BINARY', 'IMAGE']):
                    example_data[col_name] = []
                    continue
                
                try:
                    # Get most frequent values
                    query = f"""
                    SELECT `{col_name}`, COUNT(*) as freq
                    FROM `{table_name}`
                    WHERE `{col_name}` IS NOT NULL
                    GROUP BY `{col_name}`
                    ORDER BY freq DESC
                    LIMIT {number_of_rows}
                    """
                    
                    result = self.execute_query(query)
                    values = [row[col_name] for row in result]
                    
                    example_data[col_name] = values
                    
                except Exception as e:
                    logger.debug(f"Could not get example data for {table_name}.{col_name}: {e}")
                    example_data[col_name] = []
            
            return example_data
            
        except Exception as e:
            logger.error(f"Error getting example data: {e}")
            raise