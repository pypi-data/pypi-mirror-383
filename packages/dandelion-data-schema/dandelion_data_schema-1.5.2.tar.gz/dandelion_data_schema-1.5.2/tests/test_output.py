import pytest
import numpy as np
from pydantic import ValidationError

from dandelion_data_schema.output import (
    ModelOutput, ModelOutputType,
    BinaryOutput, MultiClassOutput, MultiLabelOutput, RegressionOutput
)

@pytest.mark.parametrize('output_type, output_class, kwargs', [
    (ModelOutputType.regression, RegressionOutput, {'value': 3.1415}),
    (ModelOutputType.binary, BinaryOutput, {'probability': 0.7, 'class_label': 1}),
    (ModelOutputType.multilabel, MultiLabelOutput, {'probabilities': np.array([0.1, 0.9]), 'class_labels': np.array([1, 2])}),
    (ModelOutputType.multiclass, MultiClassOutput, {'probabilities': np.array([0.2, 0.3, 0.5]), 'class_label': 2}),
])
def test_successful_creation_of_model_output(output_type, output_class, kwargs):
    model_output = output_class(
        **kwargs
    )
    assert model_output.type == output_type

    for key, value in kwargs.items():
        comparison = getattr(model_output, key) == value
        if isinstance(comparison, bool):
            assert comparison
        else:
            assert comparison.all()

@pytest.mark.parametrize('value', [
    # Missing an argument
    (None),
    # Invalid argument format
    (np.array([0.1, 0.9])),
])
def test_regression_output_cannot_be_created_with_incorrect_values(value):
    with pytest.raises(ValueError):
        RegressionOutput(probability=value)

@pytest.mark.parametrize('probability, class_label', [
    # Missing an argument
    (None, 1),
    (0.7, None),
    # Invalid argument format
    (np.array([0.1, 0.9]), 1),
    (0.7, np.array([0, 1])),
])
def test_binary_output_cannot_be_created_with_incorrect_values(probability, class_label):
    with pytest.raises(ValueError):
        BinaryOutput(probability=probability, class_label=class_label)

@pytest.mark.parametrize('probabilities, class_labels', [
    # Missing an argument
    (None, np.array([0, 1])),
    (np.array([0.1, 0.9]), None),
    # Invalid argument format
    (0, np.array([0, 1])),
    (np.array([0.1, 0.9]), 0),
    # Mismatch in argument length
    (np.array([0.1, 0.9, 0.1]), np.array([0, 1])),
    (np.array([0.1, 0.9]), np.array([0, 1, 2])),
])
def test_multilabel_output_cannot_be_created_with_incorrect_values(probabilities, class_labels):
    with pytest.raises(ValueError):
        MultiLabelOutput(probabilities=probabilities, class_labels=class_labels)

@pytest.mark.parametrize('probabilities, class_label', [
    # Missing an argument
    (None, 1),
    (0.7, None),
    # Invalid format
    (0.7, np.array([0, 1])),
    (np.array([0.1, 0.9]), np.array([0, 1])),
])
def test_multiclass_output_cannot_be_created_with_incorrect_values(probabilities, class_label):
    with pytest.raises(ValueError):
        MultiClassOutput(probabilities=probabilities, class_label=class_label)


def test_regression_type_field_validator():
    # try with incorrect field type
    with pytest.raises(ValueError):
        RegressionOutput(type=ModelOutputType.binary, value=1)


def test_binary_type_field_validator():
    # try with incorrect field type
    with pytest.raises(ValueError):
        BinaryOutput(type=ModelOutputType.regression, probability=0.7, class_label=1)


def test_multiclass_type_field_validator():
    # try with incorrect field type
    with pytest.raises(ValueError):
        MultiClassOutput(type=ModelOutputType.regression, probabilities=np.array([0.7, 0.4]), class_label=1)

def test_multilabel_type_field_validator():
    # try with incorrect field type
    with pytest.raises(ValueError):
        MultiClassOutput(type=ModelOutputType.regression, probabilities=np.array([0.7, 0.4]), class_labels=np.array([0, 1]))


def test_model_output_serialization_is_successful():
    model_output = RegressionOutput(value=1.0)
    model_output_dict = model_output.model_dump()
    assert 'type' in model_output_dict
    assert 'value' in model_output_dict
    assert model_output_dict['type'] == 'regression'
    assert model_output_dict['value'] == 1

@pytest.mark.parametrize('aux', [
    np.array([0.1, 0.4]),
    [0.1, 0.4],
])
def test_output_aux_serialization_is_successful(aux):
    model_output = RegressionOutput(aux=aux, value=1.0)
    model_output_dict = model_output.model_dump()
    assert 'type' in model_output_dict
    assert 'value' in model_output_dict
    assert model_output_dict['type'] == 'regression'
    assert model_output_dict['value'] == 1
    assert model_output_dict['aux'] == [0.1, 0.4]


def test_model_output_dump_to_json_is_successful():
    model_output = BinaryOutput(probability=0.7, class_label=1)
    model_output_json = model_output.model_dump_json()
    assert 'type' in model_output_json
    assert 'probability' in model_output_json
    assert 'class_label' in model_output_json
    assert '"type":"binary"' in model_output_json
    assert '"probability":0.7' in model_output_json
    assert '"class_label":1' in model_output_json
