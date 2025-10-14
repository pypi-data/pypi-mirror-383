"""
SHAP Explainer Module
"""

# Import necessary libraries
import shap


def shap_explainer(model, X):
    """
    SHAP Explainer Function
    ----------------------------------
    This function creates a SHAP explainer for the given model and dataset.
    It computes SHAP values for the dataset using the provided model.
    :param model: Trained machine learning model
    :type model: Any
    :param X: Input dataset for which SHAP values are to be computed
    :type X: pd.DataFrame or np.ndarray
    :return: SHAP values object
    :rtype: shap.Explanation
    """
    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)
    return shap_values
