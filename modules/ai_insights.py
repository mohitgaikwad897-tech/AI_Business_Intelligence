import pandas as pd
import numpy as np


def generate_ai_insights(
    df,
    quality_score=None,
    outlier_summary=None,
    correlation_matrix=None,
    strong_correlations=None,
    forecast_change=None
):
    """
    Generate automatic business insights from the dataset.
    """

    insights = []

    # ========================================================
    # DATASET SIZE
    # ========================================================

    rows = len(df)
    columns = len(df.columns)

    insights.append(
        f"📊 The dataset contains {rows:,} rows "
        f"across {columns:,} columns."
    )

    # ========================================================
    # DATA QUALITY
    # ========================================================

    if quality_score is not None:

        if quality_score >= 90:

            insights.append(
                f"✅ Data quality is excellent with a "
                f"score of {quality_score:.1f}/100."
            )

        elif quality_score >= 70:

            insights.append(
                f"⚠️ Data quality is acceptable with a "
                f"score of {quality_score:.1f}/100, "
                f"but some improvements may be useful."
            )

        else:

            insights.append(
                f"🚨 Data quality needs attention. "
                f"The current score is "
                f"{quality_score:.1f}/100."
            )

    # ========================================================
    # MISSING VALUES
    # ========================================================

    missing_values = int(
        df.isna().sum().sum()
    )

    if missing_values == 0:

        insights.append(
            "✅ No missing values were detected "
            "in the cleaned dataset."
        )

    else:

        insights.append(
            f"⚠️ The dataset contains "
            f"{missing_values:,} missing values."
        )

    # ========================================================
    # DUPLICATES
    # ========================================================

    duplicate_rows = int(
        df.duplicated().sum()
    )

    if duplicate_rows > 0:

        insights.append(
            f"🔄 {duplicate_rows:,} duplicate rows "
            f"were detected."
        )

    else:

        insights.append(
            "✅ No duplicate rows were detected."
        )

    # ========================================================
    # NUMERICAL COLUMNS
    # ========================================================

    numerical_columns = (
        df
        .select_dtypes(include=np.number)
        .columns
        .tolist()
    )

    if numerical_columns:

        insights.append(
            f"🔢 The dataset contains "
            f"{len(numerical_columns)} numerical "
            f"variables suitable for statistical analysis."
        )

    # ========================================================
    # OUTLIERS
    # ========================================================

    if (
        outlier_summary is not None
        and not outlier_summary.empty
    ):

        total_outliers = int(
            outlier_summary["Outliers"].sum()
        )

        if total_outliers > 0:

            insights.append(
                f"🚨 {total_outliers:,} statistical "
                f"outliers were detected across the "
                f"numerical variables."
            )

        else:

            insights.append(
                "✅ No statistical outliers were detected."
            )

    # ========================================================
    # STRONG CORRELATIONS
    # ========================================================

    if (
        strong_correlations is not None
        and not strong_correlations.empty
    ):

        for _, row in strong_correlations.head(3).iterrows():

            variable_1 = row["Variable 1"]
            variable_2 = row["Variable 2"]
            correlation = row["Correlation"]
            relationship = row["Relationship"]

            insights.append(
                f"🔗 {variable_1} and {variable_2} "
                f"show a {relationship.lower()} "
                f"relationship with a correlation of "
                f"{correlation:.2f}."
            )

    else:

        insights.append(
            "ℹ️ No strong relationships above the "
            "0.70 correlation threshold were detected."
        )

    # ========================================================
    # FORECAST
    # ========================================================

    if forecast_change is not None:

        if forecast_change > 5:

            insights.append(
                f"📈 The forecast indicates an expected "
                f"increase of approximately "
                f"{forecast_change:.2f}%."
            )

        elif forecast_change < -5:

            insights.append(
                f"📉 The forecast indicates an expected "
                f"decline of approximately "
                f"{abs(forecast_change):.2f}%."
            )

        else:

            insights.append(
                "➡️ The forecast indicates a relatively "
                "stable trend."
            )

    return insights