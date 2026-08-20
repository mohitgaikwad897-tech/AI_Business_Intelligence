import pandas as pd
import numpy as np
import plotly.graph_objects as go


def prepare_time_series(df, date_column, value_column):
    """
    Prepare a clean time-series dataset for forecasting.
    """

    data = df[[date_column, value_column]].copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data[value_column] = pd.to_numeric(
        data[value_column],
        errors="coerce"
    )

    data = data.dropna(
        subset=[date_column, value_column]
    )

    data = (
        data
        .groupby(date_column, as_index=False)[value_column]
        .sum()
        .sort_values(date_column)
    )

    return data


def create_forecast(
    df,
    date_column,
    value_column,
    periods=30
):
    """
    Create a simple trend-based forecast.

    This is intentionally lightweight and suitable
    for the first forecasting version of the dashboard.
    """

    data = prepare_time_series(
        df,
        date_column,
        value_column
    )

    if len(data) < 3:
        return None, None

    # Convert dates to numeric values
    x = (
        data[date_column]
        - data[date_column].min()
    ).dt.days

    y = data[value_column].values

    # Linear trend
    slope, intercept = np.polyfit(
        x,
        y,
        1
    )

    # Future dates
    last_date = data[date_column].max()

    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=periods,
        freq="D"
    )

    future_x = (
        future_dates
        - data[date_column].min()
    ).days

    forecast_values = (
        slope * future_x
        + intercept
    )

    forecast_df = pd.DataFrame(
        {
            date_column: future_dates,
            value_column: forecast_values
        }
    )

    return data, forecast_df


def create_forecast_chart(
    historical_df,
    forecast_df,
    date_column,
    value_column
):
    """
    Create a Plotly chart showing historical
    and forecasted values.
    """

    fig = go.Figure()

    # Historical data
    fig.add_trace(
        go.Scatter(
            x=historical_df[date_column],
            y=historical_df[value_column],
            mode="lines+markers",
            name="Historical"
        )
    )

    # Forecast
    fig.add_trace(
        go.Scatter(
            x=forecast_df[date_column],
            y=forecast_df[value_column],
            mode="lines",
            name="Forecast",
            line=dict(
                dash="dash"
            )
        )
    )

    fig.update_layout(
        title=f"{value_column} Forecast",
        xaxis_title=date_column,
        yaxis_title=value_column,
        hovermode="x unified"
    )

    return fig