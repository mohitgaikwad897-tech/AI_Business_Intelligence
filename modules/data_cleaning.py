import pandas as pd
import numpy as np


def analyze_data(df):
    """
    Analyze the dataset before cleaning.
    """

    analysis = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "numerical_columns": df.select_dtypes(
            include=np.number
        ).columns.tolist(),
        "categorical_columns": df.select_dtypes(
            include="object"
        ).columns.tolist()
    }

    return analysis


def clean_data(df):
    """
    Automatically clean the dataset.
    """

    df = df.copy()

    # ========================================================
    # AUTOMATIC DATE DETECTION AND CONVERSION
    # ========================================================

    for column in df.columns:

        if pd.api.types.is_string_dtype(df[column]):

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.80:

                df[column] = converted

    # ========================================================
    # REMOVE DUPLICATE ROWS
    # ========================================================

    df = df.drop_duplicates()

    # ========================================================
    # NUMERICAL COLUMNS
    # ========================================================

    numerical_columns = df.select_dtypes(
        include=np.number
    ).columns

    # ========================================================
    # FILL MISSING NUMERICAL VALUES
    # ========================================================

    for column in numerical_columns:

        if df[column].isna().sum() > 0:

            median_value = df[column].median()

            df[column] = df[column].fillna(
                median_value
            )

    # ========================================================
    # CATEGORICAL COLUMNS
    # ========================================================

    categorical_columns = df.select_dtypes(
        include="object"
    ).columns

    # ========================================================
    # FILL MISSING CATEGORICAL VALUES
    # ========================================================

    for column in categorical_columns:

        if df[column].isna().sum() > 0:

            mode_value = df[column].mode()

            if not mode_value.empty:

                df[column] = df[column].fillna(
                    mode_value[0]
                )

    return df
def get_data_quality_score(df):
    """
    Calculate an overall data quality score.
    """

    total_cells = df.shape[0] * df.shape[1]

    if total_cells == 0:
        return 0

    missing_cells = df.isna().sum().sum()

    duplicate_rows = df.duplicated().sum()

    missing_ratio = missing_cells / total_cells

    duplicate_ratio = (
        duplicate_rows / df.shape[0]
        if df.shape[0] > 0
        else 0
    )

    score = 100

    score -= missing_ratio * 60
    score -= duplicate_ratio * 40

    score = max(0, min(100, score))

    return round(score, 2)
def detect_date_columns(df):
    """
    Detect columns that contain date/time information.
    """

    date_columns = []

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[column]):

            date_columns.append(column)

        elif pd.api.types.is_string_dtype(df[column]):

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.80:

                date_columns.append(column)

    return date_columns