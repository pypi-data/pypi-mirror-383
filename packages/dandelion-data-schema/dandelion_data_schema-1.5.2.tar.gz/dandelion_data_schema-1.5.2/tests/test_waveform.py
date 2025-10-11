from pydantic import ValidationError
import pytest

from dandelion_data_schema.study import WaveformStudy

def test_waveform_with_valid_8_columns(waveform_array_8_columns):
    waveform = WaveformStudy(
        waveform=waveform_array_8_columns,
        sampling_frequency=100,
        signal_names=['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'],
        # studytime can be unix time
        studytime=0
    )
    assert waveform.waveform.shape[1] == 8

def test_waveform_with_valid_12_columns(waveform_array_12_columns):
    waveform = WaveformStudy(
        waveform=waveform_array_12_columns,
        sampling_frequency=100,
        signal_names=['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6'],
        # studytime can be unix time
        studytime=0
    )
    assert waveform.waveform.shape[1] == 12

def test_waveform_with_invalid_columns(invalid_waveform_array):
    with pytest.raises(ValidationError) as exc_info:
        WaveformStudy(waveform=invalid_waveform_array, studytime=0)
    assert exc_info.type == ValidationError

def test_waveform_with_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        WaveformStudy(waveform='not a numpy array', studytime=0)
    assert exc_info.type == ValidationError
