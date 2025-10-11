"""Data models for reports, which are text notes written in response to a study."""
from datetime import datetime

import numpy as np
from pydantic import BaseModel, ConfigDict, model_validator, Field


class Report(BaseModel):
    """A report is a text note written in response to a study."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders = {
            np.ndarray: lambda v: v.tolist(),
        },
    )
    studytime: datetime = Field(..., description='The time the study was performed.')
    text: str = Field(..., description='The text of the report.')

    @model_validator(mode='after')
    def validate_text(self) -> 'Report':
        """Validate that the report text is not empty."""
        if len(self.text) == 0:
            raise ValueError('report text must not be empty')
        return self