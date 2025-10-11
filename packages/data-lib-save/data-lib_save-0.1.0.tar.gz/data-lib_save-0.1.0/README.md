# data-lib_save

A library for storing, processing, and transmitting data (JSON, HTTP).

## Installation

pip install dataflow


## Usage example

```python
from dataflow.storage import DataStorage

storage = DataStorage()
storage.load()
storage.add_unique({"name": "Alice", "age": 30})