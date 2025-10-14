"""
Interactive visualizations for model explanations using Plotly.
"""

# Import necessary libraries
import plotly.express as px


def plot_feature_importance(importances, features):
    """
    Plots feature importance using Plotly.
    :param importances: A list or array of feature importances.
    :type importances: list or array
    :param features: A list of feature names.
    :type features: list
    :return: None: Displays an interactive bar chart of feature importances.
    """
    fig = px.bar(x=features, y=importances, title="Feature Importance")
    fig.show()
