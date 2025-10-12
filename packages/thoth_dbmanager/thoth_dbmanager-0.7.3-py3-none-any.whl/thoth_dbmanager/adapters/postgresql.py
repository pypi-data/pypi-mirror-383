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
PostgreSQL adapter implementation.
"""
import logging
from typing import Any, Dict, List, Optional, Union
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
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


class PostgreSQLAdapter(DbAdapter):
    """
    PostgreSQL database adapter implementation.
    """
    
    def __init__(self, connection_params: Dict[str, Any]):
        super().__init__(connection_params)
        self.engine = None
        self.raw_connection = None
        # Schema support (default 'public')
        self.schema = connection_params.get('schema', 'public')
    
    def connect(self) -> None:
        """Establish PostgreSQL connection"""
        try:
            # Create SQLAlchemy engine
            connection_string = self._build_connection_string()
            self.engine = create_engine(connection_string, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Also create raw psycopg2 connection for specific operations
            self.raw_connection = psycopg2.connect(**self._get_psycopg2_params())
            
            self._initialized = True
            logger.info("PostgreSQL connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection"""
        try:
            if self.engine:
                self.engine.dispose()
                self.engine = None
            
            if self.raw_connection:
                self.raw_connection.close()
                self.raw_connection = None
            
            self._initialized = False
            logger.info("PostgreSQL connection closed")
            
        except Exception as e:
            logger.error(f"Error closing PostgreSQL connection: {e}")
    
    def _build_connection_string(self) -> str:
        """Build SQLAlchemy connection string"""
        params = self.connection_params
        host = params.get('host', 'localhost')
        port = params.get('port', 5432)
        database = params.get('database')
        user = params.get('user')
        password = params.get('password')
        
        if not all([database, user, password]):
            raise ValueError("Missing required connection parameters: database, user, password")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def _get_psycopg2_params(self) -> Dict[str, Any]:
        """Get parameters for psycopg2 connection"""
        return {
            'host': self.connection_params.get('host', 'localhost'),
            'port': self.connection_params.get('port', 5432),
            'database': self.connection_params.get('database'),
            'user': self.connection_params.get('user'),
            'password': self.connection_params.get('password')
        }
    
    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """Execute SQL query"""
        if not self.engine:
            raise RuntimeError("Not connected to database")
        
        try:
            with self.engine.connect() as conn:
                # Set query timeout
                conn.execute(text(f"SET statement_timeout = {timeout * 1000}"))  # PostgreSQL uses milliseconds
                
                # Execute query
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                
                # Handle different fetch modes
                if query.strip().upper().startswith(('SELECT', 'WITH')):
                    if fetch == "all":
                        return result.fetchall()
                    elif fetch == "one":
                        return result.fetchone()
                    elif isinstance(fetch, int):
                        return result.fetchmany(fetch)
                    else:
                        return result.fetchall()
                else:
                    # For non-SELECT queries, return rowcount
                    conn.commit()
                    return result.rowcount
                    
        except SQLAlchemyError as e:
            logger.error(f"PostgreSQL query error: {e}")
            raise
    
    def get_tables_as_documents(self) -> List[TableDocument]:
        """Get tables as document objects"""
        # Use pg_catalog to avoid requiring SELECT privileges on tables
        # relkind: 'r' = ordinary table, 'p' = partitioned table
        query = """
        SELECT 
            n.nspname AS schema_name,
            c.relname AS table_name,
            COALESCE(d.description, '') AS comment
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_description d ON d.objoid = c.oid AND d.objsubid = 0
        WHERE c.relkind IN ('r','p')
          AND n.nspname = :schema
          AND n.nspname NOT IN ('pg_catalog','information_schema','pg_toast')
        ORDER BY c.relname
        """
        
        results = self.execute_query(query, {"schema": self.schema})
        documents = []
        
        for row in results:
            doc = TableDocument(
                table_name=row.table_name,
                schema_name=row.schema_name,
                comment=row.comment or ""
            )
            documents.append(doc)
        
        return documents
   
    
    def get_columns_as_documents(self, table_name: str) -> List[ColumnDocument]:
        """Get columns as document objects using pg_catalog to avoid SELECT restrictions"""
        query = """
        SELECT
            a.attname AS column_name,
            format_type(a.atttypid, a.atttypmod) AS data_type,
            (NOT a.attnotnull) AS is_nullable,
            pg_get_expr(d.adbin, d.adrelid) AS column_default,
            NULL::int AS character_maximum_length,
            COALESCE(pgd.description, '') AS comment,
            EXISTS (
                SELECT 1
                FROM pg_index i
                WHERE i.indrelid = c.oid AND i.indisprimary AND a.attnum = ANY(i.indkey)
            ) AS is_pk,
            n.nspname AS schema_name
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid
        LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
        LEFT JOIN pg_description pgd ON pgd.objoid = c.oid AND pgd.objsubid = a.attnum
        WHERE c.relname = :table_name
          AND n.nspname = :schema
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY a.attnum
        """

        results = self.execute_query(query, {"table_name": table_name, "schema": self.schema})
        documents = []
        
        for row in results:
            doc = ColumnDocument(
                table_name=table_name,
                column_name=row.column_name,
                data_type=row.data_type,
                comment=row.comment or "",
                is_pk=bool(row.is_pk),
                is_nullable=bool(row.is_nullable),
                default_value=row.column_default,
                max_length=row.character_maximum_length,
                schema_name=row.schema_name
            )
            documents.append(doc)
        
        return documents
    
    def get_foreign_keys_as_documents(self) -> List[ForeignKeyDocument]:
        """Get foreign keys as document objects"""
        query = """
        SELECT
            con.conname AS constraint_name,
            ns.nspname AS schema_name,
            rel.relname AS source_table,
            a.attname AS source_column,
            frel.relname AS target_table,
            fa.attname AS target_column
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_namespace ns ON ns.oid = rel.relnamespace
        JOIN pg_class frel ON frel.oid = con.confrelid
        JOIN unnest(con.conkey) WITH ORDINALITY AS src(attnum, ord) ON true
        JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = src.attnum
        JOIN unnest(con.confkey) WITH ORDINALITY AS dst(attnum, ord) ON dst.ord = src.ord
        JOIN pg_attribute fa ON fa.attrelid = con.confrelid AND fa.attnum = dst.attnum
        WHERE con.contype = 'f'
        AND ns.nspname = :schema
        ORDER BY ns.nspname, rel.relname, src.ord
        """
        
        results = self.execute_query(query, {"schema": self.schema})
        documents = []
        
        for row in results:
            doc = ForeignKeyDocument(
                source_table_name=row.source_table,
                source_column_name=row.source_column,
                target_table_name=row.target_table,
                target_column_name=row.target_column,
                constraint_name=row.constraint_name,
                schema_name=row.schema_name
            )
            documents.append(doc)
        
        return documents
    
    def get_schemas_as_documents(self) -> List[SchemaDocument]:
        """Get schemas as document objects"""
        query = """
        SELECT 
            schema_name,
            schema_owner as owner,
            COALESCE(obj_description(n.oid), '') as description
        FROM information_schema.schemata s
        LEFT JOIN pg_namespace n ON n.nspname = s.schema_name
        WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        ORDER BY schema_name
        """
        
        results = self.execute_query(query)
        documents = []
        
        for row in results:
            doc = SchemaDocument(
                schema_name=row.schema_name,
                description=row.description or "",
                owner=row.owner
            )
            documents.append(doc)
        
        return documents
    
    def get_indexes_as_documents(self, table_name: Optional[str] = None) -> List[IndexDocument]:
        """Get indexes as document objects"""
        base_query = """
        SELECT 
            i.relname as index_name,
            t.relname as table_name,
            n.nspname as schema_name,
            ix.indisunique as is_unique,
            ix.indisprimary as is_primary,
            am.amname as index_type,
            array_agg(a.attname ORDER BY a.attnum) as columns
        FROM pg_index ix
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_class t ON t.oid = ix.indrelid
        JOIN pg_namespace n ON n.oid = t.relnamespace
        JOIN pg_am am ON am.oid = i.relam
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
        WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        """
        
        if table_name:
            query = base_query + " AND t.relname = :table_name"
            params = {"table_name": table_name}
        else:
            query = base_query
            params = None
        
        query += " GROUP BY i.relname, t.relname, n.nspname, ix.indisunique, ix.indisprimary, am.amname ORDER BY t.relname, i.relname"
        
        results = self.execute_query(query, params)
        documents = []
        
        for row in results:
            doc = IndexDocument(
                index_name=row.index_name,
                table_name=row.table_name,
                columns=row.columns,
                is_unique=row.is_unique,
                is_primary=row.is_primary,
                index_type=row.index_type,
                schema_name=row.schema_name
            )
            documents.append(doc)
        
        return documents
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values from the database"""
        result = {}
        
        # Get all tables
        tables = self.get_tables_as_documents()
        
        for table_doc in tables:
            table_name = table_doc.table_name
            schema_name = table_doc.schema_name
            full_table_name = f"{schema_name}.{table_name}"
            
            # Get columns for this table
            columns = self.get_columns_as_documents(table_name)
            
            result[table_name] = {}
            
            for column_doc in columns:
                column_name = column_doc.column_name
                
                # Only get unique values for text/varchar columns to avoid large datasets
                if column_doc.data_type in ['text', 'varchar', 'character varying', 'char', 'character']:
                    try:
                        query = f"""
                        SELECT DISTINCT "{column_name}"
                        FROM "{schema_name}"."{table_name}"
                        WHERE "{column_name}" IS NOT NULL
                        AND LENGTH("{column_name}") > 0
                        ORDER BY "{column_name}"
                        LIMIT 1000
                        """
                        
                        values = self.execute_query(query)
                        result[table_name][column_name] = [str(row[0]) for row in values if row[0]]
                        
                    except Exception as e:
                        logger.warning(f"Could not get unique values for {full_table_name}.{column_name}: {e}")
                        result[table_name][column_name] = []
                else:
                    result[table_name][column_name] = []
        
        return result
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Retrieves the most frequent values for each column in the specified table.
        
        Args:
            table_name (str): The name of the table.
            number_of_rows (int, optional): Maximum number of example values to return per column. Defaults to 30.
            
        Returns:
            Dict[str, List[Any]]: A dictionary mapping column names to lists of example values.
        """
        # First, get the schema name for the table
        schema_query = """
        SELECT table_schema 
        FROM information_schema.tables 
        WHERE table_name = :table_name 
        AND table_schema NOT IN ('information_schema', 'pg_catalog')
        LIMIT 1
        """
        
        try:
            schema_result = self.execute_query(schema_query, {"table_name": table_name})
            if not schema_result:
                logger.warning(f"Table {table_name} not found")
                return {}
            
            schema_name = schema_result[0][0]
        except Exception as e:
            logger.error(f"Error getting schema for table {table_name}: {e}")
            return {}
        
        # Get column information
        columns_query = """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = :table_name AND table_schema = :schema_name
        ORDER BY ordinal_position
        """
        
        try:
            columns_result = self.execute_query(columns_query, {"table_name": table_name, "schema_name": schema_name})
        except Exception as e:
            logger.error(f"Error getting columns for table {schema_name}.{table_name}: {e}")
            return {}
        
        if not columns_result:
            logger.warning(f"No columns found for table {schema_name}.{table_name}")
            return {}
        
        most_frequent_values: Dict[str, List[Any]] = {}
        
        for row in columns_result:
            column_name = row[0]
            data_type = row[1]
            
            # PostgreSQL uses double quotes for identifier quoting
            quoted_column_name = f'"{column_name}"'
            quoted_schema_name = f'"{schema_name}"'
            quoted_table_name = f'"{table_name}"'
            
            # Query to get most frequent values
            query_str = f"""
                SELECT {quoted_column_name}
                FROM (
                    SELECT {quoted_column_name}, COUNT(*) as _freq
                    FROM {quoted_schema_name}.{quoted_table_name}
                    WHERE {quoted_column_name} IS NOT NULL
                    GROUP BY {quoted_column_name}
                    ORDER BY _freq DESC
                    LIMIT :num_rows
                ) as subquery
            """
            
            try:
                result = self.execute_query(query_str, {"num_rows": number_of_rows})
                values = [row[0] for row in result]
                most_frequent_values[column_name] = values
            except Exception as e:
                logger.error(f"Error fetching frequent values for {column_name} in {schema_name}.{table_name}: {e}")
                most_frequent_values[column_name] = []
        
        # Normalize list lengths
        max_length = 0
        if most_frequent_values:
            max_length = max(len(v) for v in most_frequent_values.values()) if most_frequent_values else 0
        
        for column_name in most_frequent_values:
            current_len = len(most_frequent_values[column_name])
            if current_len < max_length:
                most_frequent_values[column_name].extend([None] * (max_length - current_len))
        
        return most_frequent_values
