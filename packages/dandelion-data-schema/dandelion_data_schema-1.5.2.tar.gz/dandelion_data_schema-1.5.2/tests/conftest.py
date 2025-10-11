import base64
import pytest
import numpy as np
from dandelion_data_schema.study import ImagingStudy
import pytest
import numpy as np
import json
from pathlib import Path

import pydicom
from pydicom.data import get_testdata_file

# data which can be used as inputs to the classes
@pytest.fixture
def waveform_array_8_columns():
    return np.random.rand(1000, 8)

@pytest.fixture
def waveform_array_12_columns():
    return np.random.rand(1000, 12)

@pytest.fixture
def invalid_waveform_array():
    return np.random.rand(1000, 7)

@pytest.fixture
def synthetic_dataset() -> dict:
    data_dir = Path(__file__).parent.absolute() / 'data'
    with open(data_dir / 'dataset.json', 'r') as fp:
        return json.load(fp)


# create example data for each subclass to evaluate model validation/serialization
@pytest.fixture
def dicom_dataset():
    """Load a small test DICOM file from pydicom"""
    filepath = get_testdata_file("CT_small.dcm")
    return pydicom.dcmread(filepath)

@pytest.fixture
def imaging_study(dicom_dataset) -> ImagingStudy:
    return ImagingStudy(
        studytime='2021-01-01T00:00:00',
        dicom=[dicom_dataset]
    )