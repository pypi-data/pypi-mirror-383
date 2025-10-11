from enum import Enum


class ModalityType(str, Enum):
    waveform = "waveform"
    dicom = "dicom"
    tabular = "tabular"


class SexEnum(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class RaceEnum(str, Enum):
    white = "White"
    black = "Black or African American"
    asian = "Asian American or Pacific Islander"
    native = "American Indian or Native Alaskan"


class RaceEthnicityEnum(str, Enum):
    hispanic = "Hispanic"
    multiple_race = "Other or Multiple Race, non-Hispanic"
    american_indian = "American Indian or Alaska Native, non-Hispanic"
    white = "White, non-Hispanic"
    asian = "Asian, non-Hispanic"
    unknown = "Unknown/Declined"
    native_hawaiian = "Native Hawaiian or Other Pacific Islander, non-Hispanic"
    black = "Black or African American, non-Hispanic"


class EthnicityEnum(str, Enum):
    hispanic = "Hispanic"
    non_hispanic = "Non-Hispanic"


class ModelOutputType(str, Enum):
    """The type of problem the model is designed to solve."""

    binary = "binary"
    multiclass = "multiclass"
    multilabel = "multilabel"
    regression = "regression"
