
from enum import Enum

from pydantic import BaseModel


class LabName(Enum):
    WBC = "WBC"
    Hematocrit = "Hematocrit"
    Hemoglobin = "Hemoglobin"
    Platelets = "Platelets"
    Sodium = "Sodium"
    Potassium = "Potassium"
    Albumin = "Albumin"
    Alkaline_phosphatase = "Alkaline phosphatase"
    ALT = "ALT"
    AST = "AST"
    Total_bilirubin = "Total bilirubin"
    Total_protein = "Total protein"
    Calcium = "Calcium"
    Troponin_I = "Troponin I"
    Troponin_T = "Troponin T"
    Troponin_HS = "Troponin HS"
    CK = "CK"
    CK_MB = "CK-MB"
    BNP = "BNP"
    NT_proBNP = "NT-proBNP"
    Magnesium = "Magnesium"
    CRP = "CRP"
    D_dimer = "D-dimer"
    Digoxin_level = "Digoxin level"
    HgA1C = "HgA1C"

# create pydantic model for the labs
class Lab(BaseModel):
    name: LabName
    value: float
    units: str
    reference_range: str
    abnormal: bool = False
