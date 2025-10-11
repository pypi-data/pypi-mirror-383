import base64
from datetime import datetime
from pathlib import Path
from typing import List, Union

import numpy as np
import pydicom
from pydantic import (
    BaseModel,
    ConfigDict,
    field_serializer,
    field_validator,
    model_validator,
)
from pydicom.dataset import FileDataset
from pydicom.filebase import DicomBytesIO


class Study(BaseModel):
    studytime: datetime

    @field_serializer("studytime")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()


class PathToImagingStudy(Study):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    dicom: Path


class PathToECGXML(Study):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    ecg_xml: Path


class ImagingStudy(Study):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    # Some imaging studies are split across multiple DICOM files,
    # e.g. a CT scan will often have one DICOM file per slice.
    dicom: List[FileDataset]

    @field_validator("dicom")
    def validate_dicom(cls, v):
        if not isinstance(v, list):
            raise ValueError("dicom must be a list")
        for item in v:
            if not isinstance(item, FileDataset):
                raise ValueError(
                    "dicom must be a list of pydicom.dataset.FileDataset instances"
                )
        return v

    @field_serializer("dicom")
    def serialize_dicom(self, dicom: List[FileDataset]) -> List[str]:
        b64_encoded = []
        for item in dicom:
            with DicomBytesIO() as b:
                pydicom.dcmwrite(b, item)
                b64_encoded.append(base64.b64encode(b.getvalue()).decode("utf-8"))
        return b64_encoded

    @field_validator("dicom", mode="before")
    @classmethod
    def convert_dicom_from_bytes_to_filedataset(
        cls, b64_encoded: List[str]
    ) -> List[FileDataset]:
        """
        Serialization can convert the DICOM into a list of b64 encoded strings.
        If we detect that, we convert to the FileDataset objects.
        """
        if not isinstance(b64_encoded, list):
            raise ValueError("dicom must be a list")

        if all(isinstance(item, str) for item in b64_encoded):
            dicom_data = []
            for b64_string in b64_encoded:
                dicom_bytes = base64.b64decode(b64_string)
                dicom_data.append(pydicom.dcmread(DicomBytesIO(dicom_bytes)))
            return dicom_data

        # do nothing if it is not a list of string
        return b64_encoded


class WaveformStudy(Study):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            np.ndarray: lambda v: v.tolist(),
        },
    )

    sampling_frequency: float
    signal_names: List[str]
    waveform: np.ndarray

    @field_validator("waveform")
    def validate_waveform(cls, v):
        if not isinstance(v, np.ndarray):
            raise TypeError("Waveform must be a numpy array")
        if v.ndim != 2 or v.shape[1] not in (8, 12):
            raise ValueError("Waveform must be an Nx8 or Nx12 array")
        return v

    @model_validator(mode="before")
    def parse_waveform(cls, values):
        """
        Pre-validation hook to parse the waveform from a list to a numpy array if necessary.
        This assumes that the incoming data might be a list, otherwise no action is taken.
        """
        if "waveform" in values and isinstance(values["waveform"], list):
            values["waveform"] = np.array(values["waveform"])
        return values


class TabularStudy(Study):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            np.ndarray: lambda v: v.tolist(),
        },
    )

    column_names: List[str]
    values: np.ndarray
