from typing import Dict, List, Optional, Union, TypeVar, Annotated

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, BeforeValidator

from math import isnan
from .enum import SexEnum, RaceEnum, RaceEthnicityEnum, EthnicityEnum, ModalityType
from .lab import Lab, LabName
from .report import Report
from .study import (
    ImagingStudy,
    WaveformStudy,
    PathToImagingStudy,
    PathToECGXML,
    TabularStudy,
)


def coerce_nan_to_none(x):
    # Pandas uses NaN and Pydantic expects None for empty values
    if x is None:
        return x
    elif isnan(x):
        return None
    return x


OptionalOrEmpty = Annotated[Optional[TypeVar("T")], BeforeValidator(coerce_nan_to_none)]


class Record(BaseModel):
    model_config = ConfigDict(
        json_encoders={
            np.ndarray: lambda v: v.tolist(),
        },
    )
    record_name: str
    age_at_study_time: Optional[float] = Field(..., ge=0, description="Age in years")
    sex: Optional[SexEnum]
    race_ethnicity: Optional[RaceEthnicityEnum]
    height_cm: OptionalOrEmpty[float] = Field(
        default=None, ge=0, description="Height in centimeters"
    )
    weight_kg: OptionalOrEmpty[float] = Field(
        default=None, ge=0, description="Weight in kilograms"
    )

    # diagnosis codes
    icd10: Optional[List[str]] = Field(None, alias="icd10")

    # modality data
    modality_type: ModalityType
    modality_data: Union[
        WaveformStudy, ImagingStudy, PathToImagingStudy, PathToECGXML, TabularStudy
    ]
    modality_report: Optional[Report] = Field(None, alias="report")

    # other modality information which may also be collected
    related_ecg: Optional[List[WaveformStudy]] = Field(None, alias="ecg")
    related_ct: Optional[List[ImagingStudy]] = Field(None, alias="ct")
    related_echo: Optional[List[ImagingStudy]] = Field(None, alias="echo")

    # lab data
    related_lab: Optional[Dict[LabName, Lab]] = Field(None, alias="lab")
