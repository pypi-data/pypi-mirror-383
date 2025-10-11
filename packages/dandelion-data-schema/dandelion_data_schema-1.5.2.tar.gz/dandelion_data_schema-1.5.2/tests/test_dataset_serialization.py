import json
from pathlib import Path

import pydicom
import numpy as np

from dandelion_data_schema.record import Record

def test_load_dataset(synthetic_dataset: dict):
    dataset = Record.model_validate(synthetic_dataset)
    assert dataset.age_at_study_time == synthetic_dataset['age_at_study_time']
    assert dataset.sex == synthetic_dataset['sex']
    assert dataset.race_ethnicity == synthetic_dataset['race_ethnicity']
    np.testing.assert_array_equal(dataset.modality_data.waveform, np.array(synthetic_dataset['modality_data']['waveform']).reshape((100, 12)))

    dataset = Record(**synthetic_dataset)
    assert dataset.age_at_study_time == synthetic_dataset['age_at_study_time']

def test_save_dataset_to_json(synthetic_dataset: dict, tmp_path: Path):
    dataset = Record.model_validate(synthetic_dataset)
    dataset_json = dataset.model_dump_json()

    # Save JSON to a temporary file
    file_path = tmp_path / "dataset.json"
    file_path.write_text(dataset_json)

    # Ensure file was saved properly
    assert file_path.exists()

def test_load_dataset_from_json(synthetic_dataset: dict, tmp_path: Path):
    dataset = Record.model_validate(synthetic_dataset)
    file_path = tmp_path / "dataset.json"

    dataset_json = dataset.model_dump_json()
    file_path.write_text(dataset_json)

    # verify the file exists
    assert file_path.exists()
    
    # load the file
    with open(file_path, 'r') as fp:
        dataset_json = json.load(fp)
    dataset = Record.model_validate(dataset_json)

    # verify the data is the same
    assert dataset.age_at_study_time == synthetic_dataset['age_at_study_time']
