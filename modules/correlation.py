import pandas as pd
import numpy as np
import plotly.express as px


def calculate_correlations(df):
    """
    Calculate Pearson correlations between numerical columns.
    """

    numerical_df = df.select_dtypes(
        include=np.number
    )

    if numerical_df.shape[1] < 2:
        return pd.DataFrame()

    correlation_matrix = numerical_df.corr(
        method="pearson"
    )

    return correlation_matrix


def create_correlation_heatmap(df):
    """
    Create an interactive Plotly correlation heatmap.
    """

    correlation_matrix = calculate_correlations(df)

    if correlation_matrix.empty:
        return None

    fig = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        aspect="auto",
        title="Correlation Heatmap",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1
    )

    fig.update_layout(
        xaxis_title="Variables",
        yaxis_title="Variables"
    )

    return fig


def get_strong_correlations(df, threshold=0.7):
    """
    Find strong positive and negative correlations.
    """

    correlation_matrix = calculate_correlations(df)

    if correlation_matrix.empty:
        return pd.DataFrame()

    strong_correlations = []

    columns = correlation_matrix.columns.tolist()

    for i in range(len(columns)):

        for j in range(i + 1, len(columns)):

            column_1 = columns[i]
            column_2 = columns[j]

            correlation = correlation_matrix.loc[
                column_1,
                column_2
            ]

            if abs(correlation) >= threshold:

                relationship = (
                    "Strong Positive"
                    if correlation > 0
                    else "Strong Negative"
                )

                strong_correlations.append(
                    {
                        "Variable 1": column_1,
                        "Variable 2": column_2,
                        "Correlation": round(
                            correlation,
                            3
                        ),
                        "Relationship": relationship
                    }
                )

    return pd.DataFrame(
        strong_correlations
    )