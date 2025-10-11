import json

import pydicom
import pytest
from pydantic import ValidationError
from dandelion_data_schema.study import ImagingStudy

def test_dicom_with_valid_dataset(imaging_study: ImagingStudy):
    assert isinstance(imaging_study.dicom[0], pydicom.dataset.FileDataset)

def test_dicom_with_invalid_object():
    with pytest.raises(ValidationError) as exc_info:
        ImagingStudy(dicom='not a FileDataset instance')
    # verify the error was raised
    assert exc_info.type == ValidationError

def test_imaging_study_serialization(imaging_study: ImagingStudy):
    dataset_dict = imaging_study.model_dump()
    assert isinstance(dataset_dict, dict)
    assert 'studytime' in dataset_dict

def test_imaging_study_json(imaging_study: ImagingStudy):
    dataset_json = imaging_study.model_dump_json()
    assert isinstance(dataset_json, str)

def test_imaging_study_deserialization(imaging_study: ImagingStudy):
    dataset_dict = imaging_study.model_dump()
    deserialized = ImagingStudy.model_validate(dataset_dict)
    assert isinstance(deserialized, ImagingStudy)

def test_imaging_study_json_deserialization(imaging_study: ImagingStudy):
    # dump to json, try to reload it
    dataset_json = imaging_study.model_dump_json()
    deserialized = ImagingStudy.model_validate(json.loads(dataset_json))
    assert isinstance(deserialized, ImagingStudy)