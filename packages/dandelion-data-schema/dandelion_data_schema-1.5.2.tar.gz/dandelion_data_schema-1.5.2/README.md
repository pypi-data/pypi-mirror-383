# Dandelion Data Schema

The Dandelion Data Schema describes the structure of data used in the Data Validation Service provided by Dandelion Health.

## Example usage

Load an example dataset into python.

```python
import json
from dandelion_data_schema.record import Record

with open('tests/data/dataset.json', 'r') as fp:
    dataset = json.load(fp)

dataset = Record.model_validate(dataset)
```

## Distribute on pypi

```bash
python3 -m build --sdist --wheel
python3 -m twine upload --skip-existing dist/*
```
