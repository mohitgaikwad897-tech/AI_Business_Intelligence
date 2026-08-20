import pandas as pd
import numpy as np
import plotly.express as px


def detect_outliers(df):
    """
    Detect statistical outliers in numerical columns
    using the IQR method.
    """

    numerical_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    outlier_results = []

    for column in numerical_columns:

        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)

        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = df[
            (df[column] < lower_bound)
            | (df[column] > upper_bound)
        ]

        outlier_count = len(outliers)

        outlier_results.append(
            {
                "Column": column,
                "Outliers": outlier_count,
                "Outlier %": round(
                    (outlier_count / len(df)) * 100,
                    2
                ),
                "Lower Bound": round(
                    lower_bound,
                    2
                ),
                "Upper Bound": round(
                    upper_bound,
                    2
                )
            }
        )

    return pd.DataFrame(outlier_results)


def create_outlier_chart(df, column):
    """
    Create a Plotly box plot for a numerical column.
    """

    fig = px.box(
        df,
        y=column,
        title=f"Outlier Analysis — {column}",
        points="outliers"
    )

    fig.update_layout(
        yaxis_title=column,
        xaxis_title=""
    )

    return fig