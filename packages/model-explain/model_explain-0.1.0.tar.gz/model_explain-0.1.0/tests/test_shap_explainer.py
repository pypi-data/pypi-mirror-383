"""
Unit tests for SHAP and LIME explainers using scikit-learn models.

These tests validate the functionality of the explainers with a RandomForestClassifier
on the Iris dataset.
"""

# Import necessary libraries
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from model_explain.explainers.lime_explainer import lime_explainer
from model_explain.explainers.shap_explainer import shap_explainer


def test_lime_output_shape():
    """
    Test the output shape of the LIME explainer.
    :return: None: Asserts if the output shape is as expected.
    """
    data = load_iris()
    X = data.data
    model = RandomForestClassifier().fit(X, data.target)
    lime_exp = lime_explainer(model, X)
    assert len(lime_exp.as_list()) > 0


def test_lime_explainer_invalid_model():
    """
    Test the LIME explainer with an invalid model.
    :return: None: Asserts if the appropriate exception is raised.
    """
    data = load_iris()
    X = data.data
    try:
        lime_explainer(None, X)
    except Exception as e:
        assert isinstance(e, ValueError)


def test_shap_output_shape():
    """
    Test the output shape of the SHAP explainer.
    :return: None: Asserts if the output shape is as expected.
    """
    data = load_iris()
    X = data.data
    model = RandomForestClassifier().fit(X, data.target)
    shap_values = shap_explainer(model, X)
    assert len(shap_values.values) == len(X)


def test_shap_explainer_invalid_model():
    """
    Test the SHAP explainer with an invalid model.
    :return: None: Asserts if the appropriate exception is raised.
    """
    data = load_iris()
    X = data.data
    try:
        shap_explainer(None, X)
    except Exception as e:
        assert isinstance(e, ValueError)


def main():
    test_lime_output_shape()
    test_lime_explainer_invalid_model()
    test_shap_output_shape()
    test_shap_explainer_invalid_model()
    print("All tests passed!")


if __name__ == "__main__":
    main()
