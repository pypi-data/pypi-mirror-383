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
LSH (Locality Sensitive Hashing) module for database-independent LSH management.
"""

from .storage import LshStorageStrategy, PickleStorage
from .manager import LshManager
from .factory import LshFactory, make_db_lsh
from .core import create_minhash, skip_column, jaccard_similarity, create_lsh_index, query_lsh_index

__all__ = [
    "LshStorageStrategy",
    "PickleStorage", 
    "LshManager",
    "LshFactory",
    "make_db_lsh",
    "create_minhash",
    "skip_column", 
    "jaccard_similarity",
    "create_lsh_index",
    "query_lsh_index"
]
