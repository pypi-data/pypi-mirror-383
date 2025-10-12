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
Database adapters for Thoth SQL Database Manager.
"""

import logging

logger = logging.getLogger(__name__)

# Always available adapter (SQLite is built into Python)
from .sqlite import SQLiteAdapter

__all__ = [
    "SQLiteAdapter",
]

# Optional adapters - only import if dependencies are available
try:
    import psycopg2
    from .postgresql import PostgreSQLAdapter
    __all__.append("PostgreSQLAdapter")
except ImportError:
    logger.debug("psycopg2 not installed, PostgreSQLAdapter not available")
    PostgreSQLAdapter = None

try:
    import mariadb
    from .mariadb import MariaDBAdapter
    __all__.append("MariaDBAdapter")
except ImportError:
    logger.debug("MariaDB connector not installed, MariaDBAdapter not available")
    MariaDBAdapter = None

try:
    import pyodbc
    from .sqlserver import SQLServerAdapter
    __all__.append("SQLServerAdapter")
except ImportError:
    logger.debug("pyodbc not installed, SQLServerAdapter not available")
    SQLServerAdapter = None

try:
    from .informix_ssh import InformixSSHAdapter
    __all__.append("InformixSSHAdapter")
except ImportError:
    logger.debug("paramiko not installed, InformixSSHAdapter not available")
    InformixSSHAdapter = None
