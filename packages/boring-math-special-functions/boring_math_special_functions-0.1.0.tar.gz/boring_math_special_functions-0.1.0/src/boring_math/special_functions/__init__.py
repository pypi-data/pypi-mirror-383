# Copyright 2023-2025 Geoffrey R. Scheller
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
Mathematical special functions
==============================

special_functions.abstract
--------------------------

+-----------+---------------------------+---------------------+
| Function  | Description               | Type                |
+===========+===========================+=====================+
| ``const`` | Constant function factory | ``T -> [[T] -> T]`` |
+-----------+---------------------------+---------------------+
| ``id``    | Identity function         | ``T -> T``          |
+-----------+---------------------------+---------------------+

----

special_functions.float
-----------------------

+-------------+----------------------+--------------------+
| Function    | Description          | Type               |
+=============+======================+====================+
| ``exp(x)``  | exponential function | ``float -> float`` |
+-------------+----------------------+--------------------+
| ``sine(x)`` | sine function        | ``float -> float`` |
+-------------+----------------------+--------------------+

----

special_functions.complex
--------------------------

+------------+----------------------+------------------------+
| Function   | Description          | Type                   |
+============+======================+========================+
| ``exp(z)`` | exponential function | ``complex -> complex`` |
+------------+----------------------+------------------------+
| ``sin(z)`` | sine function        | ``complex -> complex`` |
+------------+----------------------+------------------------+

"""

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'
