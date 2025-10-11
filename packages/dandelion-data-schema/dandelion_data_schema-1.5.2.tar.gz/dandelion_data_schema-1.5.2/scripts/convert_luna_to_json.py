"""Convert a set of CT scans into the dataset object."""
from pathlib import Path
import json

from dandelion_data_schema.utils import load_dicom_folder
from dandelion_data_schema.study import ImagingStudy
from dandelion_data_schema.record import Record

# assumes data is in a folder in the base repo
DATA_FOLDER = Path(__file__).parent.parent / 'data/luna16'
OUTPUT_FOLDER = Path(__file__).parent.parent / 'data/dicom_json_dataset'

def main():
    # set folders for input/output
    data_folder = DATA_FOLDER
    output_folder = OUTPUT_FOLDER
    output_folder.mkdir(exist_ok=True)

    # load in the metadata dict
    with open(DATA_FOLDER / 'metadata.json', 'r') as fp:
        metadata = json.load(fp)
    # get list of directories in the data folder
    # assuming DICOM files stored in a folder
    for dicom_folder in data_folder.glob('**/'):
        # skip current dir
        if dicom_folder == data_folder:
            continue
        imaging_study = load_dicom_folder(dicom_folder)

        dicom_metadata = metadata[dicom_folder.name]
        record = Record(
            record_name=dicom_folder.name,
            modality_type='dicom',
            modality_data=imaging_study,
            **dicom_metadata
        )

        # save the record to json
        record_name = dicom_folder.name
        output_filename = output_folder / f'{record_name}.json'

        json_str = record.model_dump_json(indent=2)
        with open(output_filename, 'w') as fp:
            fp.write(json_str)

if __name__ == '__main__':
    main()