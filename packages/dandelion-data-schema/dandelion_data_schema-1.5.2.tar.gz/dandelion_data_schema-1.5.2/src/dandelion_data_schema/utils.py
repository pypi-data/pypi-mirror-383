from datetime import datetime
from pathlib import Path

import numpy as np
import pydicom

from .record import Record
from .enum import ModalityType
from .study import ImagingStudy

def get_waveform(data: Record) -> np.ndarray:
    """
    Extracts the waveform study from an observation.
    """
    if data.modality_type != ModalityType.waveform:
        raise ValueError('dataset does not contain a waveform study')
    return data.modality_data.waveform

def get_pixel_data(data: Record) -> np.ndarray:
    """
    Extracts the pixel data from a dataset.
    """
    if data.modality_type != ModalityType.dicom:
        raise ValueError('data does not contain a DICOM study')
    
    # combine together the pixel data from all DICOM files
    plans = []
    for i, plan in enumerate(data.modality_data.dicom):
        if hasattr(plan, 'pixel_array'):
            plans.append(plan.pixel_array)
        else:
            raise ValueError(f'DICOM plan in element {i} does not have pixel data')
    
    return np.stack(plans)

# utility to convert a folder of .dcm files into a single Record object
def load_dicom_folder(folder_path: Path) -> ImagingStudy:
    # load the dicom files in this subfolder into a list
    record_filenames = list(folder_path.glob('*.dcm'))
    if len(record_filenames) == 0:
        raise ValueError(f'No DICOM files found in {folder_path}')
    
    dicom_list = []
    for record_filename in record_filenames:
        dicom_list.append(pydicom.dcmread(record_filename))
    
    # DICOM has attributes for study date/time, but they are not always populated
    study_date = dicom_list[0].StudyDate
    study_time = dicom_list[0].StudyTime
    if study_time == '':
        studytime = datetime.strptime(study_date, '%Y%m%d')
    else:
        if len(study_time) > 6:
            study_time_fmt = '%H%M%S.%f'
        else:
            study_time_fmt = '%H%M%S'
        studytime = datetime.strptime(study_date + study_time, study_time_fmt)

    imaging_study = ImagingStudy(
        studytime=studytime,
        dicom=dicom_list,
    )
    return imaging_study