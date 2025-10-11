
import json
from pathlib import Path
from dandelion_data_schema.record import Record
from dandelion_data_schema.schema import OmitFieldGenerateJsonSchema

def test_schema_export(tmp_path: Path):
    file_path = tmp_path / "schema.json"
    schema = Record.model_json_schema(
        schema_generator=OmitFieldGenerateJsonSchema, mode='validation'
    )
    # dump to json
    with open(file_path, 'w') as fp:
        json.dump(schema, fp, indent=4)

    assert file_path.exists()
