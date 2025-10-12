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
Thoth Database Manager - A unified interface for multiple database systems.

This package provides database-agnostic operations, LSH similarity search,
and an extensible plugin architecture for managing SQL databases.
"""

# Core classes
from .ThothDbManager import ThothDbManager
from .core.factory import ThothDbFactory
from .core.interfaces import DbPlugin, DbAdapter
from .core.registry import DbPluginRegistry

# Document models
from .documents import (
    BaseThothDbDocument,
    TableDocument,
    ColumnDocument,
    QueryDocument,
    SchemaDocument,
    ForeignKeyDocument,
    IndexDocument,
    ThothDbType,
    create_document
)

# LSH functionality
from .lsh.factory import make_db_lsh
from .lsh import LshManager, LshFactory

# Dynamic import system
from .dynamic_imports import (
    import_manager,
    import_adapter,
    import_plugin,
    get_available_databases,
    import_database_components,
    DatabaseImportError,
)

# Public API - Modern Plugin Architecture Only
__all__ = [
    # Core API
    "ThothDbManager",
    "ThothDbFactory", 
    "DbPluginRegistry",
    "DbPlugin",
    "DbAdapter",
    
    # Document models
    "BaseThothDbDocument",
    "TableDocument",
    "ColumnDocument", 
    "QueryDocument",
    "SchemaDocument",
    "ForeignKeyDocument",
    "IndexDocument",
    "ThothDbType",
    "create_document",
    
    # LSH functionality
    "make_db_lsh",
    "LshManager",
    "LshFactory",
    
    # Dynamic import system
    "import_manager",
    "import_adapter", 
    "import_plugin",
    "get_available_databases",
    "import_database_components",
    "DatabaseImportError",
]

__version__ = "0.7.2"