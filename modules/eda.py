import pandas as pd
import numpy as np


# ============================================================
# DATASET SUMMARY
# ============================================================

def get_dataset_summary(df):
    """
    Generate a high-level summary of the dataset.
    """

    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "total_cells": df.shape[0] * df.shape[1],
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage": round(
            df.memory_usage(deep=True).sum() / 1024**2,
            2
        )
    }

    return summary


# ============================================================
# NUMERICAL SUMMARY
# ============================================================

def get_numerical_summary(df):
    """
    Generate statistical summary for numerical columns.
    """

    numerical_df = df.select_dtypes(
        include=np.number
    )

    if numerical_df.empty:
        return pd.DataFrame()

    summary = numerical_df.describe().T

    summary = summary.rename(
        columns={
            "count": "Count",
            "mean": "Mean",
            "std": "Std Dev",
            "min": "Minimum",
            "25%": "Q1",
            "50%": "Median",
            "75%": "Q3",
            "max": "Maximum"
        }
    )

    return summary


# ============================================================
# CATEGORICAL SUMMARY
# ============================================================

def get_categorical_summary(df):
    """
    Generate summary for categorical columns.
    """

    categorical_columns = [
        column
        for column in df.columns
        if (
            pd.api.types.is_string_dtype(df[column])
            and not pd.api.types.is_datetime64_any_dtype(
                df[column]
            )
        )
    ]

    results = []

    for column in categorical_columns:

        unique_count = df[column].nunique(
            dropna=True
        )

        mode = df[column].mode()

        most_common = (
            mode.iloc[0]
            if not mode.empty
            else "N/A"
        )

        results.append(
            {
                "Column": column,
                "Unique Values": unique_count,
                "Most Common": most_common
            }
        )

    return pd.DataFrame(results)


# ============================================================
# COLUMN INFORMATION
# ============================================================

def get_column_information(df):
    """
    Generate detailed information about every column.
    """

    results = []

    for column in df.columns:

        missing = int(
            df[column].isna().sum()
        )

        unique = int(
            df[column].nunique(
                dropna=True
            )
        )

        data_type = str(
            df[column].dtype
        )

        results.append(
            {
                "Column": column,
                "Data Type": data_type,
                "Missing Values": missing,
                "Unique Values": unique
            }
        )

    return pd.DataFrame(results)