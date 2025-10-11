import pytest
from dandelion_data_schema import RecordAssembler
from dandelion_data_schema.record import Record
from pathlib import Path
import pandas as pd
import json

dummy_manifest = {
    "record_metadata": {
        "schema_version": "1.0.0",
        "table_location": "DATA_TEAM_COHORT.DATA_CARD.RIVERAIN_VALIDATION_TESTING_DATASET",
        "modality_type": "dicom",
        "study_type": "CT",
        "read_study_from": "filesystem",
        "columns": {
            "record_name": "STUDY_ID",
            "study_date": "DICOM_STUDY_DATE",
            "study_location": "STUDY_LOCATION",
            "primary_patient_identifier": "PRIMARY_PATIENT_IDENTIFIER",
            "label_column": "TRUE_LABEL",
        },
    },
    "tabular_data": {
        "columns": {
            "race_ethnicity": "RACE_ETHNICITY",
            "age_at_study_time": "AGE_AT_STUDY_TIME",
            "height_cm": "HEIGHT_CM",
            "sex": "SEX_CD_DISPLAY",
        }
    },
}

dummy_series_files = ["123456-3.zip", "123456789-3.zip", "987465.zip", "98746543.zip"]
dummy_dataset = pd.DataFrame(
    {
        "STUDY_ID": ["A1", "B2"],
        "DICOM_STUDY_DATE": ["2018-06-17", "2018-06-17"],
        "STUDY_LOCATION": [
            '[\n  "s3://random_folder/123456-3.zip",\n  "s3://random_folder/123456789-3.zip"\n]',
            '[\n  "s3://random_folder/987465.zip",\n  "s3://random_folder/98746543.zip"\n]',
        ],
        "AGE_AT_STUDY_TIME": [30.0, 40.0],
        "RACE_ETHNICITY": ["White, non-Hispanic", "Hispanic"],
        "PRIMARY_PATIENT_IDENTIFIER": ["ABCD", "DCBA"],
        "TRUE_LABEL": [0, 1],
        "HEIGHT_CM": [160, 180],
        "SEX_CD_DISPLAY": ["Female", "Male"],
    }
)


def test_record_assembler(tmp_path_factory):
    data_folder = tmp_path_factory.mktemp("data")
    manifest_location = data_folder / Path("manifest.json")
    for f in dummy_series_files:
        (data_folder / Path(f)).touch()
    with open(manifest_location, "w") as f:
        f.write(json.dumps(dummy_manifest, indent=4))
    record_assembler = RecordAssembler(
        manifest_location,
        dummy_dataset,
        studies_location=data_folder,
    )

    for record in record_assembler.get_records():
        assert isinstance(record, Record)
    # Check that a directory with the study name has been created
    assert (data_folder / Path("A1")).exists()
    # Check that it contains a .zip file
    assert (data_folder / Path("A1") / Path("123456-3.zip")).exists()
