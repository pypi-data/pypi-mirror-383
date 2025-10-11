from enum import Enum
from typing import Dict, List, Optional, Union

import numpy as np
from pydantic import BaseModel, ConfigDict, model_validator, field_validator, field_serializer, Field

from .enum import ModelOutputType
from .version import _SCHEMA_VERSION

class ModelOutput(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    type: ModelOutputType
    aux: Union[np.ndarray, List[float]] = Field(default_factory=list, alias='aux')

    @field_serializer('aux', when_used='always')
    def serialize_aux(self, aux: np.ndarray, _info):
        if isinstance(aux, np.ndarray):
            return aux.tolist()
        else:
            return aux

    # allow the aux input to be a list of floats or a numpy array
    # but always store a numpy array in the object
    @field_validator('aux', mode='after')
    def convert_to_numpy(cls, v: Optional[Union[np.ndarray, List[float]]]) -> np.ndarray:
        return np.array(v) if isinstance(v, list) else v

class BinaryOutput(ModelOutput):
    type: ModelOutputType = Field(default=ModelOutputType.binary)
    probability: float
    class_label: int

    def __init__(self, **data):
        super().__init__(**data)
        if self.type != ModelOutputType.binary:
            raise ValueError('type must be binary')

class MultiClassOutput(ModelOutput):
    type: ModelOutputType = Field(default=ModelOutputType.multiclass)
    probabilities: list[float]
    class_label: int

    def __init__(self, **data):
        super().__init__(**data)
        if self.type != ModelOutputType.multiclass:
            raise ValueError('type must be multiclass')

class MultiLabelOutput(ModelOutput):
    type: ModelOutputType = Field(default=ModelOutputType.multilabel)
    probabilities: list[float]
    class_labels: list[int]

    # validate probabilities and class_labels are the same length
    @model_validator(mode='after')
    def validate_probabilities_and_class_labels(cls, output):
        if len(output.probabilities) != len(output.class_labels):
            raise ValueError('probabilities and class_labels must be the same length')

    def __init__(self, **data):
        super().__init__(**data)
        if self.type != ModelOutputType.multilabel:
            raise ValueError('type must be multilabel')

class RegressionOutput(ModelOutput):
    type: ModelOutputType = Field(default=ModelOutputType.regression)
    value: float

    def __init__(self, **data):
        super().__init__(**data)
        if self.type != ModelOutputType.regression:
            raise ValueError('type must be regression')