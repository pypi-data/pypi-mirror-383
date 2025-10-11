"""Convert a set of waveforms into the dataset object."""
from pathlib import Path
import json

from ecghelper.waveform import WaveformRecord

from dandelion_data_schema.record import Record
from dandelion_data_schema.study import WaveformStudy

# assumes data is in a folder in the base repo
DATA_FOLDER = Path(__file__).parent.parent / 'data/sample'
OUTPUT_FOLDER = Path(__file__).parent.parent / 'data/json_dataset'

def main():
    # set folders for input/output
    data_folder = DATA_FOLDER
    output_folder = OUTPUT_FOLDER
    output_folder.mkdir(exist_ok=True)

    # load in metadata
    with open(data_folder / 'metadata.json', 'r') as fp:
        metadata = json.load(fp)

    # get list of data files -> assumes in WFDB format
    record_files = data_folder.rglob('*.hea')

    # load in the waveform data from each record using ecghelper
    for record_filename in record_files:
        record_ext = record_filename.suffix
        record_name = record_filename.stem
        # wfdb expects you to omit the extension in the record name
        record = WaveformRecord.from_wfdb(data_folder / record_name)

        # get the waveform data
        waveform = record.data
        sampling_frequency = record.sampling_frequency

        # get the study time
        studytime = metadata[record_name]['studytime']

        # create the waveform study object
        waveform_study = WaveformStudy(
            waveform=waveform,
            studytime=studytime,
            sampling_frequency=sampling_frequency,
            signal_names=record.columns,
        )

        record = Record(
            record_name=record_name,
            modality_type='waveform',
            modality_data=waveform_study,
            # pass the rest of the metadata as kwargs
            # extra kwargs will be ignored by the class
            **metadata[record_name],
        )

        # save the record as a json
        output_filename = output_folder / f'{record_name}.json'

        json_str = record.model_dump_json(indent=2)
        with open(output_filename, 'w') as fp:
            fp.write(json_str)

if __name__ == '__main__':
    main()