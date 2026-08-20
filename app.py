import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import time

from modules.data_cleaning import (
    analyze_data,
    clean_data,
    get_data_quality_score,
    detect_date_columns
)
from modules.eda import (
    get_dataset_summary,
    get_numerical_summary,
    get_categorical_summary,
    get_column_information
)
from modules.visualizations import get_visualizations
from modules.outlier_detection import (
    detect_outliers,
    create_outlier_chart
)
from modules.correlation import (
    calculate_correlations,
    create_correlation_heatmap,
    get_strong_correlations
)
from modules.forecasting import (
    prepare_time_series,
    create_forecast,
    create_forecast_chart
)
from modules.ai_insights import generate_ai_insights


# ============================================================
# PERFORMANCE / CACHING HELPERS
# ============================================================

@st.cache_data(show_spinner=False)
def load_csv_cached(file_bytes):
    return pd.read_csv(BytesIO(file_bytes))


@st.cache_data(show_spinner=False)
def get_cleaned_df_cached(file_bytes):
    return clean_data(load_csv_cached(file_bytes))


@st.cache_data(show_spinner=False)
def get_before_analysis_cached(file_bytes):
    return analyze_data(load_csv_cached(file_bytes))


@st.cache_data(show_spinner=False)
def get_after_analysis_cached(file_bytes):
    return analyze_data(get_cleaned_df_cached(file_bytes))


@st.cache_data(show_spinner=False)
def get_quality_score_cached(file_bytes):
    return get_data_quality_score(load_csv_cached(file_bytes))


@st.cache_data(show_spinner=False)
def get_date_columns_cached(file_bytes):
    return detect_date_columns(load_csv_cached(file_bytes))


@st.cache_data(show_spinner=False)
def get_basic_stats_cached(file_bytes):
    data = load_csv_cached(file_bytes)
    return {
        "rows": int(data.shape[0]),
        "columns": int(data.shape[1]),
        "missing_values": int(data.isna().sum().sum()),
        "duplicate_rows": int(data.duplicated().sum())
    }


@st.cache_data(show_spinner=False)
def get_eda_cached(file_bytes):
    data = get_cleaned_df_cached(file_bytes)
    return (
        get_dataset_summary(data),
        get_numerical_summary(data),
        get_categorical_summary(data),
        get_column_information(data)
    )


@st.cache_data(show_spinner=False)
def get_outlier_summary_cached(file_bytes):
    return detect_outliers(get_cleaned_df_cached(file_bytes))


@st.cache_data(show_spinner=False)
def get_correlation_data_cached(file_bytes):
    data = get_cleaned_df_cached(file_bytes)
    return calculate_correlations(data), get_strong_correlations(data)


@st.cache_data(show_spinner=False)
def get_ai_insights_cached(file_bytes):
    data = get_cleaned_df_cached(file_bytes)
    quality = get_quality_score_cached(file_bytes)
    outliers = get_outlier_summary_cached(file_bytes)
    corr, strong = get_correlation_data_cached(file_bytes)
    return generate_ai_insights(
        data,
        quality_score=quality,
        outlier_summary=outliers,
        correlation_matrix=corr,
        strong_correlations=strong
    )


# ============================================================
# GLOBAL PROGRESS SYSTEM
# ============================================================

def run_with_progress(title, steps, functions):
    """
    Runs a sequence of functions with one reusable progress UI.

    steps:
        List of status messages.
    functions:
        List of zero-argument callables. Each callable represents
        one actual processing stage and returns its result.
    """
    if len(steps) != len(functions):
        raise ValueError("steps and functions must have the same length.")

    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    progress = progress_placeholder.progress(
        0,
        text=f"⚙️ {title} — starting..."
    )

    results = []

    try:
        for index, (step, function) in enumerate(zip(steps, functions), start=1):
            status_placeholder.markdown(f"**{step}**")

            result = function()
            results.append(result)

            percent = int(index / len(functions) * 100)
            progress.progress(
                percent,
                text=f"⚙️ {title} — {percent}%"
            )

        status_placeholder.success(f"✅ {title} completed successfully.")
        time.sleep(0.25)

    except Exception:
        progress.empty()
        status_placeholder.empty()
        raise

    progress_placeholder.empty()
    status_placeholder.empty()

    return results


def run_single_progress(title, steps, function):
    """Convenience wrapper for one expensive operation."""
    progress_placeholder = st.empty()
    status_placeholder = st.empty()

    progress = progress_placeholder.progress(
        0,
        text=f"⚙️ {title} — starting..."
    )

    try:
        total_steps = len(steps)

        for index, step in enumerate(steps, start=1):
            status_placeholder.markdown(f"**{step}**")

            # The real operation is performed on the final stage.
            if index == total_steps:
                result = function()

            percent = int(index / total_steps * 100)
            progress.progress(
                percent,
                text=f"⚙️ {title} — {percent}%"
            )

    except Exception:
        progress_placeholder.empty()
        status_placeholder.empty()
        raise

    status_placeholder.success(f"✅ {title} completed successfully.")
    time.sleep(0.25)

    progress_placeholder.empty()
    status_placeholder.empty()

    return result


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Business Intelligence",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS

st.markdown(
    """
    <style>
    /* =========================================================
       GLOBAL APP THEME
       ========================================================= */

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(55, 65, 81, 0.16), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(37, 99, 235, 0.10), transparent 25%),
            #0E1117;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Cleaner typography */
    h1, h2, h3 {
        letter-spacing: -0.02em;
    }

    h2 {
        margin-top: 0.35rem;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #171C24, #12161D);
        border: 1px solid #30363D;
        padding: 16px 18px;
        border-radius: 14px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.14);
        transition: transform 0.18s ease, border-color 0.18s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #4B5563;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.82rem;
        color: #9CA3AF;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.65rem;
        font-weight: 750;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #11151C 0%, #0D1117 100%);
        border-right: 1px solid #252B34;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.25rem;
    }

    section[data-testid="stSidebar"] [data-testid="stMetric"] {
        padding: 9px 10px;
        margin-bottom: 5px;
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        font-size: 1.05rem;
    }

    /* Navigation */
    section[data-testid="stSidebar"] [role="radiogroup"] {
        gap: 4px;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 9px;
        padding: 7px 9px;
        transition: background 0.15s ease;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.05);
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border-radius: 12px;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.025);
        border: 1px dashed #4B5563;
        border-radius: 12px;
    }

    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 650;
        border: 1px solid #374151;
        transition: all 0.18s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        border-color: #6B7280;
    }

    /* Progress bars */
    [data-testid="stProgress"] > div > div {
        border-radius: 999px;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363D;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Alerts */
    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    /* Expanders */
    [data-testid="stExpander"] {
        border: 1px solid #30363D;
        border-radius: 12px;
    }

    /* Dividers */
    hr {
        border-color: #252B34;
    }

    /* Small helper cards */
    .app-card {
        background: linear-gradient(145deg, #171C24, #12161D);
        border: 1px solid #30363D;
        border-radius: 14px;
        padding: 18px 20px;
        margin: 8px 0 16px 0;
    }

    .app-card-title {
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .app-card-text {
        color: #9CA3AF;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .dataset-pill {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.28);
        color: #86EFAC;
        font-size: 0.78rem;
        font-weight: 650;
    }

    /* Hide Streamlit chrome that adds no value to the dashboard */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER

st.markdown(
    """
    <div style="text-align:center; padding: 0.4rem 0 0.7rem 0;">
        <div style="font-size: 2.8rem; line-height:1;">🏆</div>
        <h1 style="font-size:2.45rem; margin:0.35rem 0 0.15rem 0;">
            AI Business Intelligence
        </h1>
        <div style="color:#9CA3AF; font-size:1rem;">
            From raw CSV data to clear, decision-ready business insights.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# SIDEBAR
# ============================================================

st.sidebar.markdown("# 🤖 AI Business Intelligence")
st.sidebar.caption("Automated Analytics Dashboard")
st.sidebar.divider()

st.sidebar.markdown("### 📁 Data Source")
st.sidebar.caption("Upload a CSV dataset to begin automatic analysis.")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"],
    help="Upload a CSV dataset for cleaning, analysis, visualization, forecasting and AI insights."
)


# ============================================================
# DATA PROCESSING
# ============================================================

if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()
    df = load_csv_cached(file_bytes)

    st.markdown(
        f"""
        <div class="app-card">
            <div class="app-card-title">✅ Dataset ready</div>
            <div class="app-card-text">
                <span class="dataset-pill">LOADED</span>
                &nbsp; {uploaded_file.name}
                &nbsp; • &nbsp; {df.shape[0]:,} rows
                &nbsp; • &nbsp; {df.shape[1]:,} columns
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.success("✅ Dataset loaded")
    st.sidebar.caption(uploaded_file.name)

    sidebar_info_col1, sidebar_info_col2 = st.sidebar.columns(2)

    with sidebar_info_col1:
        st.metric("Rows", f"{df.shape[0]:,}")

    with sidebar_info_col2:
        st.metric("Columns", f"{df.shape[1]:,}")

    file_size_bytes = uploaded_file.size

    if file_size_bytes < 1024:
        file_size_display = f"{file_size_bytes} B"
    elif file_size_bytes < 1024 * 1024:
        file_size_display = f"{file_size_bytes / 1024:.2f} KB"
    elif file_size_bytes < 1024 * 1024 * 1024:
        file_size_display = f"{file_size_bytes / (1024 * 1024):.2f} MB"
    else:
        file_size_display = f"{file_size_bytes / (1024 * 1024 * 1024):.2f} GB"

    st.sidebar.caption(f"💾 File size: {file_size_display}")

    if file_size_bytes >= 50 * 1024 * 1024:
        st.sidebar.info(
            "⚡ Large dataset mode enabled. Expensive analysis runs "
            "only when you open the relevant page."
        )

    # ========================================================
    # SIDEBAR NAVIGATION
    # ========================================================

    st.sidebar.divider()
    st.sidebar.markdown("### 🧭 Workspace")
    st.sidebar.caption("Select an analysis area below.")

    selected_page = st.sidebar.radio(
        "Go to",
        [
            "📊 Overview",
            "🧹 Data Cleaning",
            "🛡️ Data Quality",
            "📈 EDA",
            "📊 Visualizations",
            "🚨 Outliers",
            "🔗 Correlations",
            "🔮 Forecasting",
            "💡 AI Insights",
            "📄 Reports"
        ],
        label_visibility="collapsed"
    )

    # ========================================================
    # OVERVIEW
    # ========================================================

    if selected_page == "📊 Overview":

        basic_stats = get_basic_stats_cached(file_bytes)

        st.subheader("📊 Dataset Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📈 Total Rows", f"{df.shape[0]:,}")

        with col2:
            st.metric("📊 Total Columns", f"{df.shape[1]:,}")

        with col3:
            st.metric("⚠️ Missing Values", f"{basic_stats['missing_values']:,}")

        with col4:
            st.metric("🔄 Duplicate Rows", f"{basic_stats['duplicate_rows']:,}")

        st.divider()
        st.subheader("👀 Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True,
            height=350
        )

    # ========================================================
    # DATA CLEANING
    # ========================================================

    elif selected_page == "🧹 Data Cleaning":

        st.subheader("🧹 Automatic Data Cleaning")
        st.caption(
            "The system automatically detects and resolves common data-quality issues."
        )

        results = run_with_progress(
            "Data Cleaning",
            [
                "🔎 Analyzing original dataset...",
                "🧹 Cleaning missing values and duplicates...",
                "📋 Verifying cleaned dataset..."
            ],
            [
                lambda: get_before_analysis_cached(file_bytes),
                lambda: get_cleaned_df_cached(file_bytes),
                lambda: get_after_analysis_cached(file_bytes)
            ]
        )

        before_analysis, cleaned_df, after_analysis = results

        clean_col1, clean_col2, clean_col3, clean_col4 = st.columns(4)

        with clean_col1:
            st.metric("Original Rows", f"{before_analysis['rows']:,}")

        with clean_col2:
            duplicates_removed = (
                before_analysis["duplicate_rows"]
                - after_analysis["duplicate_rows"]
            )
            st.metric("Duplicates Removed", f"{duplicates_removed:,}")

        with clean_col3:
            st.metric("Missing Before", f"{before_analysis['missing_values']:,}")

        with clean_col4:
            st.metric("Missing After", f"{after_analysis['missing_values']:,}")

        st.divider()
        st.subheader("✨ Cleaned Dataset")

        st.dataframe(
            cleaned_df.head(10),
            use_container_width=True,
            height=350
        )

    # ========================================================
    # DATA QUALITY
    # ========================================================

    elif selected_page == "🛡️ Data Quality":

        st.subheader("🛡️ Data Quality")
        st.caption(
            "A quick assessment of the reliability of the uploaded dataset."
        )

        quality_score, date_columns = run_with_progress(
            "Data Quality Analysis",
            [
                "📊 Calculating quality score...",
                "📅 Detecting date columns..."
            ],
            [
                lambda: get_quality_score_cached(file_bytes),
                lambda: get_date_columns_cached(file_bytes)
            ]
        )

        quality_col1, quality_col2 = st.columns([2, 1])

        with quality_col1:
            st.markdown(f"### Quality Score: {quality_score}/100")
            st.progress(quality_score / 100)

            if quality_score >= 90:
                st.success("Excellent dataset quality.")
            elif quality_score >= 70:
                st.warning("Moderate data-quality issues detected.")
            else:
                st.error("Significant data-quality issues detected.")

        with quality_col2:
            numerical_count = len(
                df.select_dtypes(include=np.number).columns
            )
            categorical_count = len(
                df.select_dtypes(include="object").columns
            )

            st.metric("🔢 Numerical Columns", numerical_count)
            st.metric("🔤 Categorical Columns", categorical_count)

        st.divider()
        st.subheader("📅 Automatic Date Detection")

        if date_columns:
            st.success(
                f"Detected date column(s): {', '.join(date_columns)}"
            )
        else:
            st.info("No suitable date columns were detected.")

    # ========================================================
    # EDA
    # ========================================================

    elif selected_page == "📈 EDA":

        st.subheader("📈 Exploratory Data Analysis")
        st.caption(
            "Automatically generated statistical insights from your cleaned dataset."
        )

        (
            dataset_summary,
            numerical_summary,
            categorical_summary,
            column_information
        ) = run_single_progress(
            "Exploratory Data Analysis",
            [
                "🧹 Loading cleaned dataset...",
                "🔢 Calculating numerical statistics...",
                "🔤 Analyzing categorical columns...",
                "🧾 Building column information..."
            ],
            lambda: get_eda_cached(file_bytes)
        )

        st.markdown("### 📊 Dataset Summary")

        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

        with summary_col1:
            st.metric("Rows", f"{dataset_summary['rows']:,}")

        with summary_col2:
            st.metric("Columns", f"{dataset_summary['columns']:,}")

        with summary_col3:
            st.metric("Missing Values", f"{dataset_summary['missing_values']:,}")

        with summary_col4:
            st.metric("Memory Usage", f"{dataset_summary['memory_usage']} MB")

        st.divider()

        st.markdown("### 🔢 Numerical Analysis")

        if not numerical_summary.empty:
            st.dataframe(numerical_summary, use_container_width=True)
        else:
            st.info("No numerical columns found.")

        st.divider()

        st.markdown("### 🔤 Categorical Analysis")

        if not categorical_summary.empty:
            st.dataframe(categorical_summary, use_container_width=True)
        else:
            st.info("No categorical columns found.")

        st.divider()

        st.markdown("### 🧾 Column Information")
        st.dataframe(column_information, use_container_width=True)

    # ========================================================
    # VISUALIZATIONS
    # ========================================================

    elif selected_page == "📊 Visualizations":

        st.subheader("📊 Automatic Visualizations")
        st.caption(
            "Automatically generated charts based on your cleaned dataset."
        )

        cleaned_df, date_columns = run_with_progress(
            "Visualization Preparation",
            [
                "🧹 Loading cleaned dataset...",
                "📅 Detecting date columns..."
            ],
            [
                lambda: get_cleaned_df_cached(file_bytes),
                lambda: get_date_columns_cached(file_bytes)
            ]
        )

        plot_df = (
            cleaned_df.sample(20000, random_state=42)
            if len(cleaned_df) > 20000
            else cleaned_df
        )

        visualizations = run_single_progress(
            "Automatic Visualization Generation",
            [
                "📊 Selecting suitable columns...",
                "📈 Building automatic charts...",
                "🎨 Preparing interactive visuals..."
            ],
            lambda: get_visualizations(plot_df, date_columns)
        )

        if visualizations:
            for visualization in visualizations:
                st.markdown(f"### {visualization['title']}")
                st.plotly_chart(
                    visualization["figure"],
                    use_container_width=True
                )
                st.divider()
        else:
            st.info(
                "Not enough suitable columns were found to generate visualizations."
            )

        st.subheader("🎛️ Interactive Visualization")
        st.caption("Choose your own columns and chart type.")

        numerical_columns = cleaned_df.select_dtypes(
            include=np.number
        ).columns.tolist()

        all_columns = cleaned_df.columns.tolist()

        if all_columns:

            control_col1, control_col2, control_col3 = st.columns(3)

            with control_col1:
                chart_type = st.selectbox(
                    "📊 Chart Type",
                    ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram"]
                )

            with control_col2:
                x_column = st.selectbox("X-Axis", all_columns)

            with control_col3:
                if chart_type == "Histogram":
                    y_column = None
                elif numerical_columns:
                    y_column = st.selectbox("Y-Axis", numerical_columns)
                else:
                    y_column = None

            if chart_type == "Histogram":
                interactive_fig = px.histogram(
                    plot_df,
                    x=x_column,
                    title=f"Distribution of {x_column}"
                )
                st.plotly_chart(
                    interactive_fig,
                    use_container_width=True
                )

            elif y_column is not None:

                if chart_type == "Bar Chart":
                    interactive_fig = px.bar(
                        plot_df,
                        x=x_column,
                        y=y_column,
                        title=f"{y_column} by {x_column}"
                    )
                elif chart_type == "Line Chart":
                    interactive_fig = px.line(
                        plot_df,
                        x=x_column,
                        y=y_column,
                        title=f"{y_column} over {x_column}"
                    )
                else:
                    interactive_fig = px.scatter(
                        plot_df,
                        x=x_column,
                        y=y_column,
                        title=f"{y_column} vs {x_column}"
                    )

                st.plotly_chart(
                    interactive_fig,
                    use_container_width=True
                )

        else:
            st.info("No columns are available for visualization.")

    # ========================================================
    # OUTLIERS
    # ========================================================

    elif selected_page == "🚨 Outliers":

        st.subheader("🚨 Outlier Detection")
        st.caption("Statistical outliers detected using the IQR method.")

        cleaned_df, outlier_summary = run_with_progress(
            "Outlier Detection",
            [
                "🧹 Loading cleaned dataset...",
                "🚨 Detecting statistical outliers..."
            ],
            [
                lambda: get_cleaned_df_cached(file_bytes),
                lambda: get_outlier_summary_cached(file_bytes)
            ]
        )

        if not outlier_summary.empty:

            st.markdown("### 📊 Outlier Summary")
            st.dataframe(outlier_summary, use_container_width=True)

            st.divider()

            total_outliers = int(outlier_summary["Outliers"].sum())
            columns_with_outliers = int(
                (outlier_summary["Outliers"] > 0).sum()
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric("🚨 Total Outliers", f"{total_outliers:,}")

            with col2:
                st.metric(
                    "📊 Columns With Outliers",
                    f"{columns_with_outliers:,}"
                )

            st.divider()
            st.markdown("### 📦 Outlier Visualization")

            numerical_columns = cleaned_df.select_dtypes(
                include=np.number
            ).columns.tolist()

            if numerical_columns:

                selected_column = st.selectbox(
                    "Select a numerical column",
                    numerical_columns,
                    key="outlier_column"
                )

                outlier_fig = run_single_progress(
                    "Outlier Chart",
                    [
                        "📊 Preparing selected column...",
                        "📦 Building outlier visualization..."
                    ],
                    lambda: create_outlier_chart(
                        cleaned_df,
                        selected_column
                    )
                )

                st.plotly_chart(
                    outlier_fig,
                    use_container_width=True
                )

        else:
            st.info(
                "No numerical columns found for outlier detection."
            )

    # ========================================================
    # CORRELATIONS
    # ========================================================

    elif selected_page == "🔗 Correlations":

        st.subheader("🔗 Correlation Analysis")
        st.caption(
            "Explore relationships between numerical variables."
        )

        cleaned_df, correlation_results = run_with_progress(
            "Correlation Analysis",
            [
                "🧹 Loading cleaned dataset...",
                "🔗 Calculating correlation matrix..."
            ],
            [
                lambda: get_cleaned_df_cached(file_bytes),
                lambda: get_correlation_data_cached(file_bytes)
            ]
        )

        correlation_matrix, strong_correlations = correlation_results

        if not correlation_matrix.empty:

            st.markdown("### 📊 Correlation Matrix")
            st.dataframe(
                correlation_matrix,
                use_container_width=True
            )

            st.divider()
            st.markdown("### 🔥 Correlation Heatmap")

            correlation_fig = run_single_progress(
                "Correlation Heatmap",
                [
                    "📊 Preparing numerical relationships...",
                    "🔥 Building heatmap..."
                ],
                lambda: create_correlation_heatmap(cleaned_df)
            )

            if correlation_fig is not None:
                st.plotly_chart(
                    correlation_fig,
                    use_container_width=True
                )

            st.divider()
            st.markdown("### 🔎 Strong Relationships")
            st.caption(
                "Relationships with an absolute correlation of 0.70 or higher."
            )

            if not strong_correlations.empty:
                st.dataframe(
                    strong_correlations,
                    use_container_width=True
                )
            else:
                st.info("No strong correlations were detected.")

        else:
            st.info(
                "At least two numerical columns are required for correlation analysis."
            )

    # ========================================================
    # FORECASTING
    # ========================================================

    elif selected_page == "🔮 Forecasting":

        st.subheader("🔮 Forecasting")
        st.caption(
            "Generate a simple trend-based forecast from your time-series data."
        )

        cleaned_df, date_columns = run_with_progress(
            "Forecast Preparation",
            [
                "🧹 Loading cleaned dataset...",
                "📅 Detecting usable date columns..."
            ],
            [
                lambda: get_cleaned_df_cached(file_bytes),
                lambda: get_date_columns_cached(file_bytes)
            ]
        )

        forecast_date_columns = [
            column for column in date_columns
            if column in cleaned_df.columns
        ]

        forecast_numerical_columns = (
            cleaned_df.select_dtypes(include=np.number)
            .columns.tolist()
        )

        if not forecast_date_columns:
            st.warning(
                "No usable date column was detected. Forecasting requires a date column."
            )

        elif not forecast_numerical_columns:
            st.warning(
                "No numerical columns were detected. Forecasting requires a numerical value column."
            )

        else:

            st.markdown("### ⚙️ Forecast Settings")

            forecast_col1, forecast_col2, forecast_col3 = st.columns(3)

            with forecast_col1:
                selected_date_column = st.selectbox(
                    "📅 Date Column",
                    forecast_date_columns,
                    key="forecast_date_column"
                )

            with forecast_col2:
                selected_value_column = st.selectbox(
                    "📈 Value to Forecast",
                    forecast_numerical_columns,
                    key="forecast_value_column"
                )

            with forecast_col3:
                forecast_periods = st.number_input(
                    "🔮 Forecast Days",
                    min_value=1,
                    max_value=365,
                    value=30,
                    step=1,
                    key="forecast_periods"
                )

            if st.button(
                "🚀 Generate Forecast",
                key="generate_forecast"
            ):

                historical_data, forecast_data = run_single_progress(
                    "Forecast Generation",
                    [
                        "📅 Preparing time-series data...",
                        "🔮 Generating forecast...",
                        "📊 Preparing forecast results..."
                    ],
                    lambda: create_forecast(
                        cleaned_df,
                        selected_date_column,
                        selected_value_column,
                        periods=forecast_periods
                    )
                )

                if historical_data is None or forecast_data is None:

                    st.warning(
                        "Not enough valid historical data to generate a forecast."
                    )

                else:

                    st.markdown("### 📊 Forecast Results")

                    forecast_fig = run_single_progress(
                        "Forecast Chart",
                        [
                            "📈 Preparing historical data...",
                            "🔮 Adding forecast...",
                            "🎨 Building chart..."
                        ],
                        lambda: create_forecast_chart(
                            historical_data,
                            forecast_data,
                            selected_date_column,
                            selected_value_column
                        )
                    )

                    st.plotly_chart(
                        forecast_fig,
                        use_container_width=True
                    )

                    st.markdown("### 📌 Forecast Summary")

                    historical_average = (
                        historical_data[selected_value_column].mean()
                    )

                    forecast_average = (
                        forecast_data[selected_value_column].mean()
                    )

                    forecast_change = (
                        (
                            forecast_average - historical_average
                        )
                        / historical_average
                        * 100
                        if historical_average != 0
                        else 0
                    )

                    forecast_start = forecast_data[selected_date_column].min()
                    forecast_end = forecast_data[selected_date_column].max()

                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

                    with metric_col1:
                        st.metric(
                            "Historical Average",
                            f"{historical_average:,.2f}"
                        )

                    with metric_col2:
                        st.metric(
                            "Forecast Average",
                            f"{forecast_average:,.2f}"
                        )

                    with metric_col3:
                        st.metric(
                            "Forecast Change",
                            f"{forecast_change:+.2f}%"
                        )

                    with metric_col4:
                        st.metric(
                            "Forecast Period",
                            f"{forecast_start:%d %b} – {forecast_end:%d %b %Y}"
                        )

                    if forecast_change > 5:
                        st.success(
                            f"📈 The forecast indicates an upward trend of approximately "
                            f"{forecast_change:.2f}%."
                        )
                    elif forecast_change < -5:
                        st.warning(
                            f"📉 The forecast indicates a downward trend of approximately "
                            f"{abs(forecast_change):.2f}%."
                        )
                    else:
                        st.info(
                            "➡️ The forecast indicates a relatively stable trend."
                        )

                    st.markdown("### 🔮 Forecasted Values")
                    st.dataframe(
                        forecast_data,
                        use_container_width=True
                    )

    # ========================================================
    # AI INSIGHTS
    # ========================================================

    elif selected_page == "💡 AI Insights":

        st.subheader("💡 AI Business Insights")
        st.caption(
            "Automatically generated insights based on your cleaned dataset and statistical analysis."
        )

        ai_insights = run_single_progress(
            "AI Insight Generation",
            [
                "🧹 Preparing cleaned dataset...",
                "📊 Gathering quality and statistical analysis...",
                "🔗 Reviewing correlations and outliers...",
                "💡 Generating business insights..."
            ],
            lambda: get_ai_insights_cached(file_bytes)
        )

        if ai_insights:

            st.markdown("### 🔎 Key Insights")

            for insight in ai_insights:
                st.info(insight)

        else:
            st.warning(
                "No insights could be generated for this dataset."
            )

    # ========================================================
    # REPORTS
    # ========================================================

    elif selected_page == "📄 Reports":

        st.subheader("📄 Business Intelligence Report")
        st.caption(
            "Consolidated summary of your cleaned dataset and analysis."
        )

        report_data = run_single_progress(
            "Report Preparation",
            [
                "📊 Gathering dataset statistics...",
                "🧹 Preparing cleaned data analysis...",
                "📈 Preparing EDA results...",
                "🚨 Preparing outlier analysis...",
                "🔗 Preparing correlation analysis...",
                "💡 Preparing AI insights..."
            ],
            lambda: (
                get_basic_stats_cached(file_bytes),
                get_before_analysis_cached(file_bytes),
                get_cleaned_df_cached(file_bytes),
                get_quality_score_cached(file_bytes),
                get_date_columns_cached(file_bytes),
                get_after_analysis_cached(file_bytes),
                get_eda_cached(file_bytes),
                get_outlier_summary_cached(file_bytes),
                get_correlation_data_cached(file_bytes),
                get_ai_insights_cached(file_bytes)
            )
        )

        (
            basic_stats,
            before_analysis,
            cleaned_df,
            quality_score,
            date_columns,
            after_analysis,
            eda_results,
            outlier_summary,
            correlation_results,
            ai_insights
        ) = report_data

        (
            dataset_summary,
            numerical_summary,
            categorical_summary,
            column_information
        ) = eda_results

        correlation_matrix, strong_correlations = correlation_results

        st.markdown("### 📊 Executive Summary")

        total_outliers = (
            int(outlier_summary["Outliers"].sum())
            if (
                not outlier_summary.empty
                and "Outliers" in outlier_summary.columns
            )
            else 0
        )

        report_col1, report_col2, report_col3, report_col4 = st.columns(4)

        with report_col1:
            st.metric("Rows", f"{dataset_summary['rows']:,}")

        with report_col2:
            st.metric("Columns", f"{dataset_summary['columns']:,}")

        with report_col3:
            st.metric("Quality Score", f"{quality_score}/100")

        with report_col4:
            st.metric("Outliers", f"{total_outliers:,}")

        st.divider()

        st.markdown("### 📋 Dataset Information")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.write(f"**Rows:** {df.shape[0]:,}")
            st.write(f"**Columns:** {df.shape[1]:,}")
            st.write(
                f"**Numerical Columns:** "
                f"{len(cleaned_df.select_dtypes(include=np.number).columns)}"
            )

        with info_col2:
            st.write(
                f"**Missing Values:** {basic_stats['missing_values']:,}"
            )
            st.write(
                f"**Duplicate Rows:** {basic_stats['duplicate_rows']:,}"
            )
            st.write(
                f"**Detected Date Columns:** {len(date_columns)}"
            )

        st.divider()

        st.markdown("### 🛡️ Data Quality")

        if quality_score >= 90:
            st.success(f"Excellent data quality — {quality_score}/100")
        elif quality_score >= 70:
            st.warning(f"Moderate data quality — {quality_score}/100")
        else:
            st.error(f"Poor data quality — {quality_score}/100")

        quality_col1, quality_col2, quality_col3 = st.columns(3)

        with quality_col1:
            st.metric(
                "Missing Before Cleaning",
                f"{before_analysis['missing_values']:,}"
            )

        with quality_col2:
            st.metric(
                "Missing After Cleaning",
                f"{after_analysis['missing_values']:,}"
            )

        with quality_col3:
            duplicates_removed = (
                before_analysis["duplicate_rows"]
                - after_analysis["duplicate_rows"]
            )
            st.metric(
                "Duplicates Removed",
                f"{max(duplicates_removed, 0):,}"
            )

        st.divider()

        st.markdown("### 📈 Numerical Analysis")

        if not numerical_summary.empty:
            st.dataframe(
                numerical_summary,
                use_container_width=True
            )
        else:
            st.info("No numerical analysis available.")

        st.markdown("### 🔤 Categorical Analysis")

        if not categorical_summary.empty:
            st.dataframe(
                categorical_summary,
                use_container_width=True
            )
        else:
            st.info("No categorical analysis available.")

        st.divider()

        st.markdown("### 🚨 Outlier Analysis")

        if not outlier_summary.empty:
            st.metric(
                "Total Detected Outliers",
                f"{total_outliers:,}"
            )
            st.dataframe(
                outlier_summary,
                use_container_width=True
            )
        else:
            st.info("No numerical outlier analysis available.")

        st.divider()

        st.markdown("### 🔗 Correlation Analysis")

        if not strong_correlations.empty:
            st.dataframe(
                strong_correlations,
                use_container_width=True
            )
        else:
            st.info("No strong relationships were detected.")

        st.divider()

        st.markdown("### 💡 AI Insights")

        if ai_insights:
            for insight in ai_insights:
                st.info(insight)
        else:
            st.info("No AI insights were generated.")

        st.divider()

        # ====================================================
        # REPORT DOWNLOADS
        # ====================================================

        st.markdown("### 📥 Download Report")

        report_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AI Business Intelligence Report</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; color: #222; }}
h1 {{ color: #1f4e79; }}
h2 {{ color: #1f4e79; margin-top: 28px; }}
table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
th {{ background: #1f4e79; color: white; padding: 7px; text-align: left; }}
td {{ border: 1px solid #ddd; padding: 7px; }}
.card {{ display: inline-block; border: 1px solid #ddd; padding: 12px; margin: 5px; }}
.insight {{ background: #eef5fb; padding: 10px; margin: 8px 0; }}
</style>
</head>
<body>
<h1>📊 AI Business Intelligence Report</h1>
<p>Automatically generated from the uploaded dataset.</p>

<h2>Executive Summary</h2>
<div class="card"><b>Rows</b><br>{dataset_summary['rows']:,}</div>
<div class="card"><b>Columns</b><br>{dataset_summary['columns']:,}</div>
<div class="card"><b>Quality</b><br>{quality_score}/100</div>
<div class="card"><b>Outliers</b><br>{total_outliers:,}</div>

<h2>Dataset Information</h2>
<p>Rows: {df.shape[0]:,}</p>
<p>Columns: {df.shape[1]:,}</p>
<p>Missing Values: {basic_stats['missing_values']:,}</p>
<p>Duplicate Rows: {basic_stats['duplicate_rows']:,}</p>
<p>Date Columns: {len(date_columns)}</p>

<h2>Data Quality</h2>
<p>Quality Score: {quality_score}/100</p>
<p>Missing Before Cleaning: {before_analysis['missing_values']:,}</p>
<p>Missing After Cleaning: {after_analysis['missing_values']:,}</p>

<h2>Numerical Analysis</h2>
{numerical_summary.to_html(index=False, border=0) if not numerical_summary.empty else '<p>No numerical analysis available.</p>'}

<h2>Categorical Analysis</h2>
{categorical_summary.to_html(index=False, border=0) if not categorical_summary.empty else '<p>No categorical analysis available.</p>'}

<h2>Outlier Analysis</h2>
{outlier_summary.to_html(index=False, border=0) if not outlier_summary.empty else '<p>No outlier analysis available.</p>'}

<h2>Strong Correlations</h2>
{strong_correlations.to_html(index=False, border=0) if not strong_correlations.empty else '<p>No strong correlations detected.</p>'}

<h2>AI Insights</h2>
{''.join(f'<div class="insight">💡 {str(i)}</div>' for i in ai_insights) if ai_insights else '<p>No AI insights available.</p>'}

</body>
</html>
"""

        download_col1, download_col2 = st.columns(2)

        with download_col1:
            st.download_button(
                "📥 Download HTML Report",
                data=report_html,
                file_name="AI_Business_Intelligence_Report.html",
                mime="text/html",
                use_container_width=True
            )

        with download_col2:

            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle
            )

            pdf_buffer = BytesIO()

            pdf_doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=12 * mm,
                leftMargin=12 * mm,
                topMargin=12 * mm,
                bottomMargin=12 * mm
            )

            styles = getSampleStyleSheet()

            story = [
                Paragraph(
                    "AI Business Intelligence Report",
                    styles["Title"]
                ),
                Spacer(1, 10),
                Paragraph(
                    "Executive Summary",
                    styles["Heading2"]
                )
            ]

            summary_rows = [
                ["Metric", "Value"],
                ["Rows", f"{dataset_summary['rows']:,}"],
                ["Columns", f"{dataset_summary['columns']:,}"],
                ["Quality Score", f"{quality_score}/100"],
                ["Outliers", f"{total_outliers:,}"],
                ["Missing Values", f"{basic_stats['missing_values']:,}"],
                ["Duplicate Rows", f"{basic_stats['duplicate_rows']:,}"],
            ]

            summary_table = Table(
                summary_rows,
                colWidths=[75 * mm, 75 * mm]
            )

            summary_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))

            story.append(summary_table)
            story.append(Spacer(1, 12))

            story.append(
                Paragraph(
                    "Data Quality",
                    styles["Heading2"]
                )
            )

            story.append(
                Paragraph(
                    f"Quality Score: {quality_score}/100 | "
                    f"Missing Before: {before_analysis['missing_values']:,} | "
                    f"Missing After: {after_analysis['missing_values']:,}",
                    styles["BodyText"]
                )
            )

            story.append(Spacer(1, 12))

            story.append(
                Paragraph(
                    "AI Insights",
                    styles["Heading2"]
                )
            )

            if ai_insights:
                for insight in ai_insights:
                    story.append(
                        Paragraph(
                            f"• {str(insight)}",
                            styles["BodyText"]
                        )
                    )
                    story.append(Spacer(1, 4))
            else:
                story.append(
                    Paragraph(
                        "No AI insights available.",
                        styles["BodyText"]
                    )
                )

            pdf_doc.build(story)
            pdf_buffer.seek(0)

            st.download_button(
                "📕 Download PDF Report",
                data=pdf_buffer.getvalue(),
                file_name="AI_Business_Intelligence_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

else:

    st.markdown(
        """
        <div style="max-width:850px; margin:4rem auto 0 auto; text-align:center;">
            <div style="font-size:4rem;">📊</div>
            <h2 style="margin-bottom:0.35rem;">Your analytics workspace is ready</h2>
            <p style="color:#9CA3AF; font-size:1rem; line-height:1.6;">
                Upload a CSV dataset from the sidebar to start cleaning,
                exploring, visualizing and turning your data into business insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="max-width:850px; margin:1.5rem auto;">
            <div class="app-card">
                <div class="app-card-title">🚀 What happens next?</div>
                <div class="app-card-text">
                    Upload once. The dashboard will handle data cleaning,
                    quality checks, EDA, visualizations, outlier detection,
                    correlations, forecasting, AI insights and report generation.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )