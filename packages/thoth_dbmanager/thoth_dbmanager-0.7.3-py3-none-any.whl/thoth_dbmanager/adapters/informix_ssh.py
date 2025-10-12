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
IBM Informix adapter implementation using SSH + dbaccess.

This adapter provides connectivity to Informix databases via SSH tunnel
and dbaccess command-line tool, requiring ZERO native drivers or Client SDK.
"""
import logging
import re
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import paramiko

from ..core.interfaces import DbAdapter
from ..documents import (
    TableDocument,
    ColumnDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument
)

logger = logging.getLogger(__name__)


class InformixSSHAdapter(DbAdapter):
    """
    IBM Informix database adapter using SSH + dbaccess.
    
    This adapter connects to Informix via SSH and executes queries using
    the dbaccess command-line tool on the remote server. This approach
    requires NO local drivers or Client SDK installation.
    
    Advantages:
    - Zero local dependencies (only paramiko)
    - Works on all platforms (macOS, Linux, Windows, Docker)
    - No driver installation required
    - Portable and simple
    
    Disadvantages:
    - Slight performance overhead (SSH + text parsing)
    - Requires dbaccess available on remote server
    """
    
    def __init__(self, connection_params: Dict[str, Any]):
        super().__init__(connection_params)
        
        self.ssh_client = None
        self.database = connection_params.get('database')
        
        # SSH connection parameters
        self.ssh_host = connection_params.get('ssh_host') or connection_params.get('host')
        self.ssh_port = connection_params.get('ssh_port', 22)
        self.ssh_username = connection_params.get('ssh_username') or connection_params.get('user')
        self.ssh_password = connection_params.get('ssh_password')
        # Support both naming conventions
        self.ssh_key_file = (connection_params.get('ssh_private_key_path') or 
                            connection_params.get('ssh_key_file'))
        self.ssh_key_passphrase = (connection_params.get('ssh_private_key_passphrase') or
                                   connection_params.get('ssh_key_passphrase'))
        
        # Informix server parameters (for connection string on remote)
        self.informix_server = connection_params.get('server')
        self.informix_user = connection_params.get('user')
        self.informix_password = connection_params.get('password')
        self.informix_dir = connection_params.get('informixdir', '/u/appl/ids10')  # Default path
        
        if not all([self.ssh_host, self.ssh_username, self.database]):
            raise ValueError("Missing required parameters: ssh_host, ssh_username, database")
    
    def connect(self) -> None:
        """Establish SSH connection to Informix server"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Prepare connection parameters
            connect_kwargs = {
                'hostname': self.ssh_host,
                'port': self.ssh_port,
                'username': self.ssh_username,
            }
            
            # Authentication
            if self.ssh_key_file:
                key_path = Path(self.ssh_key_file).expanduser()
                connect_kwargs['key_filename'] = str(key_path)
                if self.ssh_key_passphrase:
                    connect_kwargs['passphrase'] = self.ssh_key_passphrase
            elif self.ssh_password:
                connect_kwargs['password'] = self.ssh_password
            else:
                raise ValueError("Either ssh_key_file or ssh_password must be provided")
            
            logger.debug(f"Connecting via SSH to {self.ssh_host}:{self.ssh_port} as {self.ssh_username}")
            self.ssh_client.connect(**connect_kwargs)
            
            # Test dbaccess availability (optional - may not be in PATH)
            try:
                self._verify_dbaccess()
            except RuntimeError as e:
                logger.warning(f"dbaccess verification failed: {e}")
                logger.warning("Proceeding anyway - will fail on first query if dbaccess is not available")
            
            self._initialized = True
            logger.info(f"SSH connection established to {self.ssh_host}, database: {self.database}")
            
        except Exception as e:
            logger.error(f"Failed to establish SSH connection: {e}")
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
            raise ConnectionError(f"SSH connection failed: {e}")
    
    def disconnect(self) -> None:
        """Close SSH connection"""
        try:
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
            
            self._initialized = False
            logger.info("SSH connection closed")
            
        except Exception as e:
            logger.error(f"Error closing SSH connection: {e}")
    
    def _verify_dbaccess(self) -> None:
        """Verify dbaccess is available on remote server"""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command("which dbaccess")
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code != 0:
                raise RuntimeError(
                    "dbaccess command not found on remote server. "
                    "Ensure Informix is installed and dbaccess is in PATH."
                )
            
            dbaccess_path = stdout.read().decode('utf-8').strip()
            logger.debug(f"dbaccess found at: {dbaccess_path}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to verify dbaccess: {e}")
    
    def execute_query(self, query: str, params: Optional[Dict] = None, 
                     fetch: Union[str, int] = "all", timeout: int = 60) -> Any:
        """
        Execute SQL query via SSH + dbaccess.
        
        Args:
            query: SQL query string
            params: Query parameters (will be escaped and substituted)
            fetch: How to fetch results ('all', 'one', or number)
            timeout: Query timeout in seconds
            
        Returns:
            Query results or rowcount for non-SELECT queries
        """
        if not self.ssh_client:
            raise RuntimeError("Not connected to SSH server")
        
        try:
            # Prepare query with parameters
            if params:
                query = self._prepare_query_with_params(query, params)
            
            # Execute via dbaccess
            output = self._execute_dbaccess(query, timeout)
            
            # Parse output
            query_upper = query.strip().upper()
            if query_upper.startswith(('SELECT', 'WITH')):
                return self._parse_select_output(output, fetch)
            else:
                # For INSERT, UPDATE, DELETE - extract rowcount
                return self._parse_rowcount(output)
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            logger.error(f"Query was: {query[:200]}...")
            raise
    
    def _prepare_query_with_params(self, query: str, params: Dict) -> str:
        """Prepare query by substituting parameters safely"""
        # Simple parameter substitution with escaping
        # For production, consider more robust escaping
        prepared_query = query
        for key, value in params.items():
            placeholder = f":{key}"
            if placeholder in prepared_query:
                # Escape single quotes
                if isinstance(value, str):
                    escaped_value = value.replace("'", "''")
                    prepared_query = prepared_query.replace(placeholder, f"'{escaped_value}'")
                elif value is None:
                    prepared_query = prepared_query.replace(placeholder, "NULL")
                else:
                    prepared_query = prepared_query.replace(placeholder, str(value))
        
        return prepared_query
    
    def _execute_dbaccess(self, query: str, timeout: int = 60) -> str:
        """Execute query via dbaccess command"""
        # Escape query for shell
        query_escaped = query.replace('"', '\\"').replace('$', '\\$')
        
        # Build dbaccess command with full environment setup
        # Set INFORMIXDIR, INFORMIXSERVER, and PATH before executing
        command = (
            f"export INFORMIXDIR={self.informix_dir} && "
            f"export INFORMIXSERVER={self.informix_server or 'ns1i10'} && "
            f"export PATH=$INFORMIXDIR/bin:$PATH && "
            f'echo "{query_escaped}" | $INFORMIXDIR/bin/dbaccess {self.database}'
        )
        
        logger.debug(f"Executing dbaccess command on remote server")
        logger.debug(f"Query: {query[:100]}...")
        
        # Execute command
        stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
        
        # Get output
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        exit_code = stdout.channel.recv_exit_status()
        
        # Check for errors (but ignore stderr if exit code is 0 and output looks good)
        # Informix dbaccess may write warnings to stderr even on success
        if exit_code != 0:
            logger.error(f"dbaccess command failed with exit code {exit_code}")
            logger.error(f"Error: {error or output}")
            raise RuntimeError(f"Query execution failed: {error or output}")
        
        # Check for SQL errors in output (not just the word "error")
        if ' error ' in output.lower() or output.strip().startswith('error'):
            logger.error(f"SQL error in output: {output}")
            raise RuntimeError(f"Query execution failed: {output}")
        
        return output
    
    def _parse_select_output(self, output: str, fetch: Union[str, int]) -> Any:
        """
        Parse SELECT query output from dbaccess.
        
        Informix dbaccess can output in two formats:
        
        1. Tabular format (few rows):
        ```
         colname1 colname2 colname3
         
              val1     val2     val3
              val4     val5     val6
        ```
        
        2. Vertical format (many rows):
        ```
        colname1  value1
        colname2  value2
        colname3  value3
        
        colname1  value4
        colname2  value5
        colname3  value6
        ```
        """
        import re
        
        lines = output.strip().split('\n')
        logger.debug(f"Raw output ({len(lines)} lines)")
        
        # Remove empty lines at start and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        if not lines:
            logger.warning("No non-empty lines in output")
            return [] if fetch == "all" else None
        
        # Detect format by looking at the pattern of lines
        # Vertical format: each line is "colname  value", with blank lines between records
        # Tabular format: first line is headers, following lines are data rows
        
        # Check first few non-empty lines
        non_empty_lines = [l.strip() for l in lines if l.strip()]
        
        if len(non_empty_lines) < 1:
            logger.warning("No non-empty lines in output")
            return [] if fetch == "all" else None
        
        # Check if lines follow vertical pattern: multiple lines with "  " separator
        # and different first parts (column names)
        import re
        vertical_pattern_count = 0
        first_parts = set()
        
        for line in non_empty_lines[:10]:  # Check first 10 non-empty lines
            parts = re.split(r'\s{2,}', line)
            if len(parts) == 2:
                vertical_pattern_count += 1
                first_parts.add(parts[0])
        
        # Special case: single line with 2 parts - could be either format
        # If it's a single line, check if the first part looks like a column name
        if len(non_empty_lines) == 1 and vertical_pattern_count == 1:
            # Single line with "colname  value" - treat as vertical (single row, single column)
            logger.debug("Detected single-line vertical format (1 column, 1 row)")
            return self._parse_vertical_format(lines, fetch)
        
        # If most lines have 2 parts and we see different column names, it's vertical
        if vertical_pattern_count >= 3 and len(first_parts) >= 2:
            logger.debug(f"Detected vertical format ({vertical_pattern_count} lines with 2 parts, {len(first_parts)} unique column names)")
            return self._parse_vertical_format(lines, fetch)
        else:
            # Tabular format
            logger.debug(f"Detected tabular format ({vertical_pattern_count} lines with 2 parts, {len(first_parts)} unique column names)")
            return self._parse_tabular_format(lines, fetch)
    
    def _parse_vertical_format(self, lines: list, fetch: Union[str, int]) -> Any:
        """Parse vertical format output (column  value pairs)"""
        import re
        
        # Split into blocks by blank lines
        blocks = []
        current_block = []
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                current_block.append(stripped)
            else:
                if current_block:
                    blocks.append(current_block)
                    current_block = []
        
        if current_block:
            blocks.append(current_block)
        
        if not blocks:
            return [] if fetch == "all" else None
        
        logger.debug(f"Found {len(blocks)} blocks in vertical format")
        
        # Parse each block into a row
        rows = []
        for block_idx, block in enumerate(blocks):
            columns = []
            values = []
            
            for line in block:
                # Split by two or more spaces (handles varying spacing)
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 2:
                    col_name = parts[0].strip()
                    col_value = parts[1].strip()
                    columns.append(col_name)
                    values.append(col_value)
                elif len(parts) == 1:
                    # Single part - might be a value with no column name
                    # This shouldn't happen in vertical format, log warning
                    logger.warning(f"Unexpected single part in vertical format: {line}")
            
            if columns and values and len(columns) == len(values):
                rows.append(Row(columns, values))
            elif columns or values:
                logger.warning(f"Block {block_idx}: column/value count mismatch - {len(columns)} cols, {len(values)} vals")
        
        logger.debug(f"Parsed {len(rows)} rows from {len(blocks)} blocks (vertical format)")
        
        # Apply fetch mode
        if fetch == "one":
            return rows[0] if rows else None
        elif fetch == "all":
            return rows
        elif isinstance(fetch, int):
            return rows[:fetch]
        else:
            return rows
    
    def _parse_tabular_format(self, lines: list, fetch: Union[str, int]) -> Any:
        """Parse tabular format output (column headers + data rows)"""
        # First non-empty line should be column headers
        header_line = lines[0].strip()
        column_names = header_line.split()
        
        if not column_names:
            logger.warning("No column names found in header")
            return [] if fetch == "all" else None
        
        logger.debug(f"Column names: {column_names}")
        
        # Parse data rows (skip header and any blank lines)
        rows = []
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped:
                continue  # Skip blank lines
            
            # Split by whitespace
            values = stripped.split()
            
            # If we have the right number of values, create a row
            if len(values) == len(column_names):
                rows.append(Row(column_names, values))
            elif len(values) > 0:
                # If we have values but count doesn't match, try to handle it
                if len(values) < len(column_names):
                    values.extend([None] * (len(column_names) - len(values)))
                else:
                    values = values[:len(column_names)]
                rows.append(Row(column_names, values))
        
        logger.debug(f"Parsed {len(rows)} rows (tabular format)")
        
        # Apply fetch mode
        if fetch == "one":
            return rows[0] if rows else None
        elif fetch == "all":
            return rows
        elif isinstance(fetch, int):
            return rows[:fetch]
        else:
            return rows
    
    def _parse_rowcount(self, output: str) -> int:
        """Parse rowcount from INSERT/UPDATE/DELETE output"""
        # Look for patterns like "1 row(s) inserted" or "5 row(s) deleted"
        match = re.search(r'(\d+)\s+row\(s\)', output, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0
    
    def health_check(self) -> bool:
        """Check if database connection is healthy using Informix-compatible query"""
        try:
            # Use a simple query from system catalog
            self.execute_query("SELECT tabid FROM systables WHERE tabid = 1", fetch="one")
            return True
        except Exception:
            return False
    
    def get_tables_as_documents(self) -> List[TableDocument]:
        """
        Get tables as document objects from Informix system catalog.
        
        Uses systables system catalog to retrieve table information.
        Filters out system tables (tabid < 100) and views.
        
        Returns:
            List[TableDocument]: List of table documents
        """
        query = """
        SELECT 
            tabname,
            tabtype,
            nrows
        FROM systables 
        WHERE tabid >= 100 
          AND tabtype IN ('T', 'V')
        ORDER BY tabname
        """
        
        try:
            results = self.execute_query(query)
            documents = []
            
            for row in results:
                # Map tabtype to readable name
                tabtype = row['tabtype'].strip() if row['tabtype'] else 'T'
                table_type = 'TABLE' if tabtype == 'T' else 'VIEW' if tabtype == 'V' else tabtype
                
                doc = TableDocument(
                    table_name=row['tabname'].strip() if row['tabname'] else '',
                    table_type=table_type,
                    row_count=int(row['nrows']) if row['nrows'] and str(row['nrows']).strip() else 0,
                    schema_name=self.database,  # Informix uses database as schema
                    comment=''
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} tables from Informix")
            return documents
            
        except Exception as e:
            logger.error(f"Error getting tables from Informix: {e}")
            raise
    
    def get_columns_as_documents(self, table_name: str) -> List[ColumnDocument]:
        """
        Get columns as document objects from Informix system catalog.
        
        Uses syscolumns joined with systables to retrieve column information.
        Detects primary keys via sysconstraints and sysindexes.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List[ColumnDocument]: List of column documents
        """
        # Informix type mapping
        INFORMIX_TYPE_MAP = {
            0: 'CHAR',
            1: 'SMALLINT',
            2: 'INTEGER',
            3: 'FLOAT',
            4: 'SMALLFLOAT',
            5: 'DECIMAL',
            6: 'SERIAL',
            7: 'DATE',
            8: 'MONEY',
            9: 'NULL',
            10: 'DATETIME',
            11: 'BYTE',
            12: 'TEXT',
            13: 'VARCHAR',
            14: 'INTERVAL',
            15: 'NCHAR',
            16: 'NVARCHAR',
            17: 'INT8',
            18: 'SERIAL8',
            19: 'SET',
            20: 'MULTISET',
            21: 'LIST',
            22: 'ROW',
            40: 'LVARCHAR',
            41: 'BOOLEAN',
        }
        
        query = """
        SELECT 
            c.colname,
            c.coltype,
            c.collength,
            c.colno
        FROM syscolumns c
        JOIN systables t ON c.tabid = t.tabid
        WHERE t.tabname = '{table_name}'
          AND t.tabid >= 100
        ORDER BY c.colno
        """.format(table_name=table_name)
        
        try:
            # Execute query to get columns
            results = self.execute_query(query)
            
            # Get primary key columns (simplified - may not work for all cases)
            pk_columns = set()
            try:
                pk_query = """
                SELECT c.colname
                FROM syscolumns c
                JOIN systables t ON c.tabid = t.tabid
                JOIN sysconstraints con ON con.tabid = t.tabid
                WHERE t.tabname = '{table_name}'
                  AND con.constrtype = 'P'
                """.format(table_name=table_name)
                
                pk_results = self.execute_query(pk_query)
                pk_columns = {row['colname'].strip() for row in pk_results}
            except Exception as e:
                logger.warning(f"Could not get PK info for {table_name}: {e}")
            
            documents = []
            
            for row in results:
                col_name = row['colname'].strip() if row['colname'] else ''
                coltype = int(row['coltype']) if row['coltype'] else 0
                
                # Extract base type (remove nullable flag)
                base_type = coltype % 256 if coltype else 0
                is_nullable = coltype >= 256 if coltype else True
                
                # Map to readable type name
                type_name = INFORMIX_TYPE_MAP.get(base_type, f'UNKNOWN({base_type})')
                
                # Add length for char/varchar types
                collength = int(row['collength']) if row['collength'] else 0
                if base_type in (0, 13, 15, 16, 40):  # CHAR, VARCHAR, NCHAR, NVARCHAR, LVARCHAR
                    type_name = f"{type_name}({collength})"
                
                doc = ColumnDocument(
                    table_name=table_name,
                    column_name=col_name,
                    data_type=type_name,
                    is_nullable=is_nullable,
                    is_pk=col_name in pk_columns,
                    max_length=collength,
                    schema_name=self.database,
                    comment=''
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} columns for table {table_name}")
            return documents
            
        except Exception as e:
            logger.error(f"Error getting columns for table {table_name}: {e}")
            raise
    
    def get_foreign_keys_as_documents(self) -> List[ForeignKeyDocument]:
        """
        Get foreign keys as document objects from Informix system catalog.
        
        Uses sysconstraints, sysreferences, and syscolumns to retrieve FK relationships
        with actual column names. Handles single-column foreign keys by accessing the
        first element of the column position arrays.
        
        Note: Multi-column foreign keys are currently simplified to show only the first
        column pair. Future enhancement could iterate through all array positions.
        
        Returns:
            List[ForeignKeyDocument]: List of foreign key documents
        """
        query = """
        SELECT 
            con.constrname as constraint_name,
            t1.tabname as source_table,
            t2.tabname as target_table,
            sc1.colname as source_column,
            sc2.colname as target_column
        FROM sysconstraints con
        JOIN sysreferences ref ON con.constrid = ref.constrid
        JOIN systables t1 ON con.tabid = t1.tabid
        JOIN systables t2 ON ref.ptabid = t2.tabid
        LEFT JOIN syscolumns sc1 ON sc1.tabid = t1.tabid AND sc1.colno = ref.foreign[1]
        LEFT JOIN syscolumns sc2 ON sc2.tabid = t2.tabid AND sc2.colno = ref.primary[1]
        WHERE con.constrtype = 'R'
          AND t1.tabid >= 100
          AND t2.tabid >= 100
        ORDER BY t1.tabname, con.constrname
        """
        
        try:
            results = self.execute_query(query)
            documents = []
            
            # Process each FK relationship
            for row in results:
                source_table = row['source_table'].strip() if row.get('source_table') else ''
                target_table = row['target_table'].strip() if row.get('target_table') else ''
                constraint_name = row['constraint_name'].strip() if row.get('constraint_name') else ''
                source_column = row['source_column'].strip() if row.get('source_column') else ''
                target_column = row['target_column'].strip() if row.get('target_column') else ''
                
                # Create FK document with actual column names
                # If column names are empty, it means the array access failed or columns not found
                if not source_column or not target_column:
                    logger.warning(
                        f"FK {constraint_name}: Missing column names. "
                        f"source_column='{source_column}', target_column='{target_column}'. "
                        f"This may be a multi-column FK or array syntax issue."
                    )
                    # Still create the document but with empty column names
                    # This maintains backward compatibility
                
                doc = ForeignKeyDocument(
                    constraint_name=constraint_name,
                    source_table_name=source_table,
                    source_column_name=source_column,
                    target_table_name=target_table,
                    target_column_name=target_column,
                    schema_name=self.database
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} foreign key relationships")
            
            # Log summary of successful column name retrieval
            fks_with_columns = sum(1 for doc in documents if doc.source_column_name and doc.target_column_name)
            fks_without_columns = len(documents) - fks_with_columns
            
            if fks_with_columns > 0:
                logger.info(f"  - {fks_with_columns} FKs with column names retrieved successfully")
            if fks_without_columns > 0:
                logger.warning(f"  - {fks_without_columns} FKs without column names (may be multi-column or query issue)")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error getting foreign keys: {e}")
            logger.error("This may be due to:")
            logger.error("  1. Informix version doesn't support array syntax (ref.foreign[1], ref.primary[1])")
            logger.error("  2. No foreign keys exist in the database")
            logger.error("  3. Permissions issue accessing system tables")
            # Return empty list if FK retrieval fails
            logger.warning("Returning empty FK list due to error")
            return []
    
    def get_schemas_as_documents(self) -> List[SchemaDocument]:
        """
        Get schemas as document objects.
        
        Informix doesn't have schemas like PostgreSQL - it uses databases.
        This method returns the current database as a schema.
        
        Returns:
            List[SchemaDocument]: List containing one schema document for current database
        """
        try:
            # Get table count for current database
            table_count_query = """
            SELECT COUNT(*) as cnt
            FROM systables
            WHERE tabid >= 100 AND tabtype = 'T'
            """
            
            result = self.execute_query(table_count_query, fetch="one")
            table_count = int(result['cnt']) if result and 'cnt' in result and result['cnt'] else 0
            
            doc = SchemaDocument(
                schema_name=self.database,
                description=f"Informix database: {self.database}",
                owner=self.informix_user or 'unknown',
                table_count=table_count
            )
            
            logger.info(f"Retrieved schema document for database {self.database}")
            return [doc]
            
        except Exception as e:
            logger.error(f"Error getting schema information: {e}")
            raise
    
    def get_indexes_as_documents(self, table_name: Optional[str] = None) -> List[IndexDocument]:
        """
        Get indexes as document objects from Informix system catalog.
        
        Uses sysindexes to retrieve index information.
        Note: This is a simplified implementation.
        
        Args:
            table_name: Optional table name to filter indexes
            
        Returns:
            List[IndexDocument]: List of index documents
        """
        if table_name:
            query = """
            SELECT 
                idx.idxname,
                t.tabname,
                idx.idxtype,
                CASE 
                    WHEN idx.idxtype = 'U' THEN 1
                    ELSE 0
                END as is_unique
            FROM sysindexes idx
            JOIN systables t ON idx.tabid = t.tabid
            WHERE t.tabid >= 100
              AND t.tabname = '{table_name}'
              AND idx.idxname IS NOT NULL
              AND idx.idxname != ' '
            ORDER BY t.tabname, idx.idxname
            """.format(table_name=table_name)
        else:
            query = """
            SELECT 
                idx.idxname,
                t.tabname,
                idx.idxtype,
                CASE 
                    WHEN idx.idxtype = 'U' THEN 1
                    ELSE 0
                END as is_unique
            FROM sysindexes idx
            JOIN systables t ON idx.tabid = t.tabid
            WHERE t.tabid >= 100
              AND idx.idxname IS NOT NULL
              AND idx.idxname != ' '
            ORDER BY t.tabname, idx.idxname
            """
        
        try:
            results = self.execute_query(query)
            documents = []
            
            for row in results:
                idx_name = row['idxname'].strip() if row['idxname'] else ''
                tbl_name = row['tabname'].strip() if row['tabname'] else ''
                
                # Skip empty index names
                if not idx_name or idx_name.strip() == '':
                    continue
                
                # Check if this is a primary key index (simplified)
                is_primary = False
                try:
                    pk_query = """
                    SELECT COUNT(*) as cnt
                    FROM sysconstraints con
                    JOIN systables t ON con.tabid = t.tabid
                    WHERE con.idxname = '{idx_name}'
                      AND t.tabname = '{tbl_name}'
                      AND con.constrtype = 'P'
                    """.format(idx_name=idx_name, tbl_name=tbl_name)
                    pk_result = self.execute_query(pk_query, fetch="one")
                    is_primary = pk_result and int(pk_result['cnt']) > 0
                except Exception:
                    pass
                
                doc = IndexDocument(
                    index_name=idx_name,
                    table_name=tbl_name,
                    columns=[],  # Would need additional query to get columns
                    is_unique=bool(int(row['is_unique']) if row['is_unique'] else 0),
                    is_primary=is_primary,
                    index_type=row['idxtype'].strip() if row['idxtype'] else 'BTREE',
                    schema_name=self.database
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} indexes")
            return documents
            
        except Exception as e:
            logger.error(f"Error getting indexes: {e}")
            raise
    
    def get_unique_values(self) -> Dict[str, Dict[str, List[str]]]:
        """Get unique values - PHASE 3"""
        raise NotImplementedError("Phase 3: get_unique_values() not yet implemented")
    
    def get_example_data(self, table_name: str, number_of_rows: int = 30) -> Dict[str, List[Any]]:
        """
        Retrieves sample data from the specified table.
        
        Args:
            table_name: The name of the table
            number_of_rows: Maximum number of rows to return (default: 30)
            
        Returns:
            Dict[str, List[Any]]: Dictionary mapping column names to lists of values
        """
        try:
            # Get column information first
            columns = self.get_columns_as_documents(table_name)
            
            if not columns:
                logger.warning(f"No columns found for table {table_name}")
                return {}
            
            # Build column list for query
            column_names = [col.column_name for col in columns]
            columns_str = ', '.join(column_names)
            
            # Query to get sample data (using FIRST for Informix)
            query = f"""
            SELECT FIRST {number_of_rows} {columns_str}
            FROM {table_name}
            """
            
            result = self.execute_query(query)
            
            # Convert to column-oriented format
            example_data: Dict[str, List[Any]] = {col: [] for col in column_names}
            
            for row in result:
                for col in column_names:
                    value = row[col] if col in row else None
                    example_data[col].append(value)
            
            logger.info(f"Retrieved {len(result)} sample rows from {table_name}")
            return example_data
            
        except Exception as e:
            logger.error(f"Error getting example data for table {table_name}: {e}")
            return {}


class Row:
    """
    Row object that mimics SQLAlchemy Row behavior for dict-like access.
    """
    def __init__(self, columns: List[str], values: List[str]):
        self._columns = columns
        self._values = values
        self._mapping = {col: val for col, val in zip(columns, values)}
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return self._mapping[key]
    
    def __getattr__(self, name):
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        if name in self._mapping:
            return self._mapping[name]
        raise AttributeError(f"Row has no attribute '{name}'")
    
    def keys(self):
        return self._columns
    
    def values(self):
        return self._values
    
    def items(self):
        return self._mapping.items()
    
    def __repr__(self):
        items = ", ".join(f"{k}={v!r}" for k, v in self._mapping.items())
        return f"Row({items})"
    
    def __len__(self):
        return len(self._columns)
