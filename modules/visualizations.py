import pandas as pd
import plotly.express as px


def get_numerical_columns(df):
    """Return numerical columns."""
    return df.select_dtypes(include="number").columns.tolist()


def get_categorical_columns(df):
    """Return categorical columns."""
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


def get_visualizations(df, date_columns=None):
    """
    Automatically generate useful Plotly visualizations
    based on the structure of the cleaned dataset.
    """

    figures = []

    numerical_columns = get_numerical_columns(df)
    categorical_columns = get_categorical_columns(df)

    # --------------------------------------------------------
    # DATE / TIME-SERIES ANALYSIS
    # --------------------------------------------------------

    if date_columns:

        for date_column in date_columns[:2]:

            temp_df = df.copy()

            temp_df[date_column] = pd.to_datetime(
                temp_df[date_column],
                errors="coerce"
            )

            temp_df = temp_df.dropna(
                subset=[date_column]
            )

            if not temp_df.empty and numerical_columns:

                for numerical_column in numerical_columns[:3]:

                    chart_df = (
                        temp_df
                        .sort_values(date_column)
                    )

                    fig = px.line(
                        chart_df,
                        x=date_column,
                        y=numerical_column,
                        title=f"{numerical_column} Over Time"
                    )

                    figures.append(
                        {
                            "title": f"{numerical_column} Over Time",
                            "figure": fig
                        }
                    )

    # --------------------------------------------------------
    # NUMERICAL DISTRIBUTIONS
    # --------------------------------------------------------

    for column in numerical_columns[:5]:

        fig = px.histogram(
            df,
            x=column,
            title=f"Distribution of {column}",
            marginal="box"
        )

        figures.append(
            {
                "title": f"Distribution of {column}",
                "figure": fig
            }
        )

    # --------------------------------------------------------
    # CATEGORICAL ANALYSIS
    # --------------------------------------------------------

    for column in categorical_columns[:5]:

        value_counts = (
            df[column]
            .value_counts()
            .head(10)
            .reset_index()
        )

        value_counts.columns = [
            column,
            "Count"
        ]

        fig = px.bar(
            value_counts,
            x=column,
            y="Count",
            title=f"Top Categories — {column}"
        )

        figures.append(
            {
                "title": f"Top Categories — {column}",
                "figure": fig
            }
        )

    # --------------------------------------------------------
    # NUMERICAL RELATIONSHIP
    # --------------------------------------------------------

    if len(numerical_columns) >= 2:

        x_column = numerical_columns[0]
        y_column = numerical_columns[1]

        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=f"{x_column} vs {y_column}"
        )

        figures.append(
            {
                "title": f"{x_column} vs {y_column}",
                "figure": fig
            }
        )

    return figures
def create_interactive_chart(
    df,
    chart_type,
    x_column,
    y_column=None
):
    """Create an interactive Plotly chart."""

    if chart_type == "Bar Chart":

        return px.bar(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} by {x_column}"
        )

    elif chart_type == "Line Chart":

        return px.line(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} over {x_column}"
        )

    elif chart_type == "Scatter Plot":

        return px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} vs {x_column}"
        )

    elif chart_type == "Histogram":

        return px.histogram(
            df,
            x=x_column,
            title=f"Distribution of {x_column}"
        )

    return None