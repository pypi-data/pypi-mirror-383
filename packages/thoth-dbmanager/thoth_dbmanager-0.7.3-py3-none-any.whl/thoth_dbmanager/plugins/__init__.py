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
Database plugins for Thoth SQL Database Manager.
"""

import logging

logger = logging.getLogger(__name__)

# Always available plugin (SQLite is built into Python)
from .sqlite import SQLitePlugin

__all__ = [
    "SQLitePlugin",
]

# Optional plugins - only import if dependencies are available
try:
    import psycopg2
    from .postgresql import PostgreSQLPlugin
    __all__.append("PostgreSQLPlugin")
    logger.debug("PostgreSQL plugin loaded successfully")
except ImportError:
    logger.debug("psycopg2 not installed, PostgreSQL plugin not available")
    PostgreSQLPlugin = None

try:
    import mariadb
    from .mariadb import MariaDBPlugin
    __all__.append("MariaDBPlugin")
    logger.debug("MariaDB plugin loaded successfully")
except ImportError:
    logger.debug("MariaDB connector not installed, MariaDB plugin not available")
    MariaDBPlugin = None

try:
    import pyodbc
    from .sqlserver import SQLServerPlugin
    __all__.append("SQLServerPlugin")
    logger.debug("SQL Server plugin loaded successfully")
except ImportError:
    logger.debug("pyodbc not installed, SQL Server plugin not available")
    SQLServerPlugin = None

try:
    import paramiko
    from .informix import InformixPlugin
    __all__.append("InformixPlugin")
    logger.debug("Informix plugin loaded successfully (SSH-based, no ODBC required)")
except ImportError:
    logger.debug("paramiko not installed, Informix plugin not available")
    InformixPlugin = None
