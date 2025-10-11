import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd

from dandelion_data_schema.enum import ModalityType
from dandelion_data_schema.record import Record
from dandelion_data_schema.study import PathToImagingStudy, PathToECGXML, TabularStudy

_LOGGER = logging.getLogger(__name__)


class RecordAssembler:
    def __init__(
        self,
        manifest_location: Path,
        dataset: pd.DataFrame,
        studies_location: Path = Path(),
    ):
        """Class that generates Record objects by reading a manifest file and a dataset.

        Args:
            manifest_location (Path): Path to manifest file (.json)
            dataset (pd.DataFrame): Input dataset. Columns must match the specification from the manifest file
            studies_location (Path, optional): Location of the studies to load into Record objects. Defaults to Path().
        """
        self._record = None
        self._manifest = None
        self.dataset = dataset
        self.studies_location = studies_location
        self._read_manifest(manifest_location)

    def _read_manifest(self, manifest_location: Path):
        with open(manifest_location, "r") as f:
            self._manifest = json.load(f)

    def _extract_dataset_record_values(self, row: pd.Series):
        """For a single row in the dataset, loads it as a dictionary using the specification from the manifest as dictionary keys

        Args:
            row (pd.Series): Dataset row

        Raises:
            KeyError: _description_
            NotImplementedError: _description_

        Returns:
            _type_: _description_
        """
        # All columns that we must load from dataframe / row
        modality_data_columns = self._manifest["tabular_data"].get(
            "modality_data_columns", []
        )
        columns_to_load = {
            **self._manifest["record_metadata"]["columns"],
            **self._manifest["tabular_data"]["columns"],
            **{col: col for col in modality_data_columns},
        }
        try:
            record_values = {
                field: row[columns_to_load[field]] for field in columns_to_load
            }
        except KeyError as e:
            raise KeyError(
                f"The dataset is missing column {str(e)} specified in the manifest file"
            ) from e

        modality_data = self._create_study(record_values)
        return {
            "modality_data": modality_data,
            "modality_type": self._manifest["record_metadata"]["modality_type"],
            **{field: row[columns_to_load[field]] for field in columns_to_load},
        }

    def _create_study(self, record_values):
        read_study_from = self._manifest["record_metadata"]["read_study_from"]

        if read_study_from == "filesystem":
            return self._create_study_from_filesystem(record_values)
        elif read_study_from == "dataframe":
            return self._create_study_from_dataframe(record_values)
        else:
            raise NotImplementedError(
                f"Unsupported data source {read_study_from}. Only reading from the file system or a dataframe is supported."
            )

    def _create_study_from_filesystem(self, record_values):
        """Creates 'Study' object containing the data from the study. Currently it only supports storing the studies as pointers to directory.

        For each study, it creates a new folder using the study id as folder name. Then it moves all series in the study inside that folder.

        Args:
            record_values (_type_): _description_

        Raises:
            FileNotFoundError: _description_
            NotImplementedError: _description_

        Returns:
            _type_: _description_
        """
        # Assemble study as a folder with data inside the folder
        study_path = self.studies_location / Path(record_values["record_name"]).stem
        study_path.mkdir(parents=True, exist_ok=True)
        try:
            series_paths = json.loads(record_values["study_location"])
        except json.JSONDecodeError:
            series_paths = [record_values["study_location"]]
        for series in series_paths:
            input_series_path = self.studies_location / Path(series).name
            output_series_path = study_path / Path(series).name
            try:
                Path(input_series_path).rename(output_series_path)
            except FileNotFoundError as e:
                # Either file does not exist or it has already been moved
                if output_series_path.is_file():
                    _LOGGER.info(
                        "File %s already in objective directory",
                        output_series_path,
                    )
                else:
                    raise FileNotFoundError(
                        f"File {input_series_path} not found"
                    ) from e

        modality_type = self._manifest["record_metadata"]["modality_type"]
        if modality_type == ModalityType.dicom:
            return PathToImagingStudy(
                dicom=study_path, studytime=record_values["study_date"]
            )
        elif modality_type == ModalityType.waveform:
            return PathToECGXML(
                ecg_xml=study_path, studytime=record_values["study_date"]
            )
        else:
            raise NotImplementedError(f"Modality type {modality_type} unsupported")

    def _create_study_from_dataframe(self, record_values):
        modality_type = self._manifest["record_metadata"]["modality_type"]
        if modality_type != ModalityType.tabular:
            raise NotImplementedError(
                f"Reading modality type {modality_type} from a dataframe is unsupported."
            )
        modality_data = {
            field: record_values[field]
            for field in self._manifest["tabular_data"]["modality_data_columns"]
        }
        column_names = list(modality_data.keys())
        values = [modality_data[key] for key in column_names]
        return TabularStudy(
            column_names=column_names,
            values=np.array(values),
            studytime=record_values["study_date"],
        )

    def get_records(self):
        for _, row in self.dataset.iterrows():
            yield Record(
                **self._extract_dataset_record_values(row),
            )
