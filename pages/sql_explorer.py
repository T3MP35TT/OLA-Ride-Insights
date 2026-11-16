"""Explicitly triggered, read-only SQL explorer with complete result handling."""
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import show_chart, show_insight, show_table
from utils.sidebar import set_sidebar_context
from utils.sql_engine import COLUMN_MAP, MAX_ROWS, execute_readonly_query
from utils.sql_queries import QUESTIONS

PREVIEW_ROWS = 500
CUSTOM = "Custom SQL query"
DEFAULT_CUSTOM = "SELECT booking_status, COUNT(*) AS bookings\nFROM bookings\nGROUP BY booking_status\nORDER BY bookings DESC;"
LABELS = {f"{number:02d}. {question}": question for number, question in enumerate(QUESTIONS, 1)}


def _format_number(value):
    numeric = float(value)
    return f"{numeric:,.0f}" if numeric.is_integer() else f"{numeric:,.2f}"


def _question_changed():
    selected = st.session_state["sql_question"]
    st.session_state["sql_editor"] = DEFAULT_CUSTOM if selected == CUSTOM else QUESTIONS[LABELS[selected]][0]
    for key in ("sql_last_result", "sql_last_query", "sql_last_error", "sql_last_question_label",
                "sql_chart_group", "sql_chart_measure", "sql_chart_type", "sql_chart_aggregation", "sql_numeric_measure"):
        st.session_state.pop(key, None)


def _executed_label(query, selected, label):
    if selected == CUSTOM:
        return CUSTOM
    expected = QUESTIONS[label][0]
    normalize = lambda sql: " ".join(str(sql).strip().rstrip(";").split()).casefold()
    return label if normalize(query) == normalize(expected) else CUSTOM


def _topline(result):
    """Summarize actual result values without guessing a top group from raw rows."""
    if result.empty:
        return [("Rows returned", "0"), ("Result fields", str(len(result.columns)))]
    numeric = list(result.select_dtypes(include="number").columns)
    if len(result) == 1 and numeric:
        return [
            (column.replace("_", " ").title(), _format_number(result.iloc[0][column]) if pd.notna(result.iloc[0][column]) else "Not available")
            for column in numeric[:4]
        ]
    metrics = [("Rows returned", f"{len(result):,}")]
    for column in numeric[:3]:
        values = pd.to_numeric(result[column], errors="coerce").dropna()
        if values.empty:
            continue
        label = column.replace("_", " ").title()
        span = _format_number(values.min()) if values.min() == values.max() else f"{_format_number(values.min())} to {_format_number(values.max())}"
        metrics.append((f"{label} range", span))
    return metrics[:4]


def _question_metrics(result, label, df, fields):
    """Return business KPIs for a named question; generic custom SQL is handled separately."""
    status_col = fields.get("status")
    status = df[status_col].astype("string").str.strip().str.casefold() if status_col else pd.Series(dtype="string")
    booking_total = len(df)

    if label == "Successful bookings":
        values = pd.to_numeric(result.get("booking_value", pd.Series(dtype=float)), errors="coerce")
        return [("Successful bookings", f"{len(result):,}"),
                ("Completed booking value", _format_number(values.sum())),
                ("Average booking value", _format_number(values.mean()) if values.notna().any() else "Unavailable"),
                ("Customers", f"{result['customer_id'].nunique():,}" if "customer_id" in result else "Unavailable")]

    if label == "Average ride distance by vehicle" and not result.empty:
        measure = "average_ride_distance"
        valid = result.dropna(subset=[measure])
        high = valid.loc[valid[measure].idxmax()] if not valid.empty else None
        low = valid.loc[valid[measure].idxmin()] if not valid.empty else None
        return [("Vehicle types", f"{result['vehicle_type'].nunique():,}"),
                ("Highest mean distance", f"{high['vehicle_type']}: {_format_number(high[measure])}" if high is not None else "Unavailable"),
                ("Lowest mean distance", f"{low['vehicle_type']}: {_format_number(low[measure])}" if low is not None else "Unavailable"),
                ("Trips with distance", f"{int(result['trips_with_distance'].sum()):,}")]

    if label == "Customer cancellations" and not result.empty:
        count = int(result.iloc[0, 0])
        return [("Customer cancellations", f"{count:,}"),
                ("Share of bookings", f"{count / booking_total:.1%}" if booking_total else "Unavailable"),
                ("Bookings in scope", f"{booking_total:,}")]

    if label == "Top five customers by rides" and not result.empty:
        lead = result.iloc[0]
        return [("Top customer", str(lead["customer_id"])),
                ("Bookings · top customer", f"{int(lead['bookings']):,}"),
                ("Bookings · top five", f"{int(result['bookings'].sum()):,}")]

    if label == "Driver personal/car cancellations" and not result.empty:
        count = int(result.iloc[0, 0])
        driver_total = int(status.eq("canceled by driver").sum()) if status_col else 0
        return [("Personal/car cancellations", f"{count:,}"),
                ("Share of driver cancellations", f"{count / driver_total:.1%}" if driver_total else "Unavailable"),
                ("Driver cancellations", f"{driver_total:,}")]

    if label == "Prime Sedan driver rating range" and not result.empty:
        maximum = result.iloc[0]["maximum_driver_rating"]
        minimum = result.iloc[0]["minimum_driver_rating"]
        vehicle_col, rating_col = fields.get("vehicle"), fields.get("driver_rating")
        if vehicle_col and rating_col:
            prime = df[vehicle_col].astype("string").str.strip().str.casefold().eq("prime sedan")
            observations = pd.to_numeric(df.loc[prime, rating_col], errors="coerce").notna().sum()
        else:
            observations = 0
        return [("Maximum driver rating", _format_number(maximum)),
                ("Minimum driver rating", _format_number(minimum)),
                ("Observed ratings", f"{observations:,}")]

    if label == "UPI bookings":
        values = pd.to_numeric(result.get("booking_value", pd.Series(dtype=float)), errors="coerce")
        return [("UPI bookings", f"{len(result):,}"),
                ("UPI booking value", _format_number(values.sum())),
                ("Average UPI booking value", _format_number(values.mean()) if values.notna().any() else "Unavailable"),
                ("Customers", f"{result['customer_id'].nunique():,}" if "customer_id" in result else "Unavailable")]

    if label == "Average customer rating by vehicle" and not result.empty:
        valid = result.dropna(subset=["average_customer_rating"])
        high = valid.loc[valid["average_customer_rating"].idxmax()] if not valid.empty else None
        low = valid.loc[valid["average_customer_rating"].idxmin()] if not valid.empty else None
        return [("Highest mean rating", f"{high['vehicle_type']}: {_format_number(high['average_customer_rating'])}" if high is not None else "Unavailable"),
                ("Lowest mean rating", f"{low['vehicle_type']}: {_format_number(low['average_customer_rating'])}" if low is not None else "Unavailable"),
                ("Observed feedback", f"{int(result['rated_trips'].sum()):,}")]

    if label == "Completed booking value" and not result.empty:
        total_value = float(result.iloc[0]["completed_booking_value"] or 0)
        count = int(status.eq("success").sum()) if status_col else 0
        return [("Completed booking value", _format_number(total_value)),
                ("Successful bookings", f"{count:,}"),
                ("Average per successful booking", _format_number(total_value / count) if count else "Unavailable")]

    if label == "Incomplete rides and reason":
        reason_col = "incomplete_rides_reason"
        reason_counts = result[reason_col].fillna("Reason missing").value_counts() if reason_col in result else pd.Series(dtype=int)
        if reason_counts.empty:
            return [("Incomplete rides", f"{len(result):,}"), ("Share of bookings", f"{len(result) / booking_total:.1%}" if booking_total else "Unavailable")]
        return [("Incomplete rides", f"{len(result):,}"),
                ("Most common reason", str(reason_counts.index[0])),
                ("Bookings · leading reason", f"{int(reason_counts.iloc[0]):,}"),
                ("Share of bookings", f"{len(result) / booking_total:.1%}" if booking_total else "Unavailable")]

    return _topline(result)


def _business_chart(result, label, df, fields):
    """Build the default chart for each predefined question from its answer data."""
    if result.empty:
        return None, None

    if label == "Successful bookings" and "vehicle_type" in result:
        chart = result.groupby("vehicle_type", dropna=False).agg(
            Successful_bookings=("booking_id", "size"),
            Completed_booking_value=("booking_value", "sum"),
        ).reset_index()
        fig = px.bar(chart.sort_values("Successful_bookings"), x="Successful_bookings", y="vehicle_type", orientation="h",
                     color="Successful_bookings", hover_data={"Completed_booking_value": ":,.0f"},
                     title="Successful bookings and completed value by vehicle")
        insight = "Booking counts use all successful rows. Hover for completed booking value; recorded value is not audited revenue."
        return fig, insight

    if label == "Average ride distance by vehicle":
        fig = px.bar(result.sort_values("average_ride_distance"), x="average_ride_distance", y="vehicle_type", orientation="h",
                     color="average_ride_distance", hover_data={"trips_with_distance": ":,"},
                     title="Average ride distance by vehicle")
        return fig, "Bars compare means; hover shows contributing non-null trips. Distance units are unspecified in the source."

    if label == "Customer cancellations":
        status_col = fields.get("status")
        if not status_col:
            return None, None
        chart = df[status_col].fillna("Missing").astype(str).str.strip().value_counts().rename_axis("Booking outcome").reset_index(name="Bookings")
        chart["Focus"] = chart["Booking outcome"].str.casefold().eq("canceled by customer").map({True: "Customer cancellation", False: "Other outcome"})
        fig = px.bar(chart.sort_values("Bookings"), x="Bookings", y="Booking outcome", orientation="h", color="Focus",
                     color_discrete_map={"Customer cancellation": "#E89E25", "Other outcome": "#7D9400"},
                     title="Customer cancellations within all booking outcomes")
        return fig, "The highlighted bar is the query result. Rates use all bookings; driver cancellations and driver-not-found remain separate outcomes."

    if label == "Top five customers by rides":
        fig = px.bar(result.sort_values("bookings"), x="bookings", y="customer_id", orientation="h", color="bookings",
                     title="Top five customers by booking count")
        return fig, "Each bar is one customer’s booking count; IDs are anonymous source identifiers, not customer profiles."

    if label == "Driver personal/car cancellations":
        status_col, reason_col = fields.get("status"), fields.get("driver_reason")
        if not status_col or not reason_col:
            return None, None
        status = df[status_col].astype("string").str.strip().str.casefold()
        reasons = df.loc[status.eq("canceled by driver"), reason_col].fillna("Reason missing").astype(str).value_counts()
        chart = reasons.rename_axis("Driver cancellation reason").reset_index(name="Bookings")
        chart["Query match"] = chart["Driver cancellation reason"].str.casefold().str.contains("personal", regex=False) & chart["Driver cancellation reason"].str.casefold().str.contains("car", regex=False)
        chart["Query match"] = chart["Query match"].map({True: "Personal/car query", False: "Other driver reason"})
        fig = px.bar(chart.sort_values("Bookings"), x="Bookings", y="Driver cancellation reason", orientation="h", color="Query match",
                     color_discrete_map={"Personal/car query": "#E89E25", "Other driver reason": "#7D9400"},
                     title="Driver cancellation reasons · query category highlighted")
        return fig, "The highlighted reason category matches the SQL filters for both 'personal' and 'car'."

    if label == "Prime Sedan driver rating range":
        vehicle_col, rating_col = fields.get("vehicle"), fields.get("driver_rating")
        if not vehicle_col or not rating_col:
            return None, None
        prime = df[vehicle_col].astype("string").str.strip().str.casefold().eq("prime sedan")
        ratings = pd.to_numeric(df.loc[prime, rating_col], errors="coerce").dropna()
        chart = ratings.value_counts().sort_index().rename_axis("Driver rating").reset_index(name="Feedback records")
        fig = px.bar(chart, x="Driver rating", y="Feedback records", title="Prime Sedan driver rating distribution")
        return fig, "Only observed Prime Sedan driver ratings are counted; the KPI range does not imply a rating target."

    if label == "UPI bookings" and "vehicle_type" in result:
        chart = result.groupby("vehicle_type", dropna=False).agg(
            UPI_bookings=("booking_id", "size"),
            UPI_booking_value=("booking_value", "sum"),
        ).reset_index()
        fig = px.bar(chart.sort_values("UPI_bookings"), x="UPI_bookings", y="vehicle_type", orientation="h", color="UPI_bookings",
                     hover_data={"UPI_booking_value": ":,.0f"}, title="UPI bookings by vehicle")
        return fig, "Booking counts and recorded booking value cover all UPI rows returned by the SQL query."

    if label == "Average customer rating by vehicle":
        fig = px.bar(result.sort_values("average_customer_rating"), x="average_customer_rating", y="vehicle_type", orientation="h",
                     color="average_customer_rating", hover_data={"rated_trips": ":,"}, title="Observed customer rating by vehicle")
        fig.update_xaxes(range=[3, 5])
        return fig, "Hover shows feedback counts. Compare ratings alongside coverage; unobserved feedback is excluded."

    if label == "Completed booking value":
        status_col, payment_col, value_col = fields.get("status"), fields.get("payment"), fields.get("value")
        if not status_col or not payment_col or not value_col:
            return None, None
        success = df[status_col].astype("string").str.strip().str.casefold().eq("success")
        chart = df.loc[success].groupby(payment_col, dropna=False).agg(
            Completed_booking_value=(value_col, "sum"), Successful_bookings=(value_col, "size"),
        ).reset_index()
        fig = px.bar(chart.sort_values("Completed_booking_value"), x="Completed_booking_value", y=payment_col, orientation="h",
                     color="Completed_booking_value", hover_data={"Successful_bookings": ":,"},
                     title="Completed booking value by payment method")
        return fig, "Payment breakdown sums successful bookings only. Source currency and accounting recognition are not defined."

    if label == "Incomplete rides and reason" and "incomplete_rides_reason" in result:
        chart = result["incomplete_rides_reason"].fillna("Reason missing").value_counts().rename_axis("Incomplete ride reason").reset_index(name="Bookings")
        fig = px.bar(chart.sort_values("Bookings"), x="Bookings", y="Incomplete ride reason", orientation="h", color="Bookings",
                     title="Source-flagged incomplete rides by reason")
        return fig, "This chart uses rows flagged Incomplete_Rides = Yes; incomplete rides are separate from cancellation statuses."

    return None, None


def _visualize_custom(result, label):
    numeric = list(result.select_dtypes(include="number").columns)
    dimensions = [column for column in result.columns if column not in numeric]
    if result.empty:
        st.info("This query returned no records for the selected conditions.")
        return

    if dimensions:
        cardinality = result[dimensions].nunique(dropna=False)
        threshold = min(100, max(15, int(len(result) * .2)))
        dimensions = sorted(
            [column for column in dimensions if cardinality[column] <= threshold],
            key=lambda column: cardinality[column],
        )
    if not dimensions:
        if numeric:
            if len(result) == 1:
                st.info("This is a scalar SQL result. Its exact value is shown above; a chart would not add a useful comparison.")
                return
            measure = st.selectbox("Numeric field to inspect", numeric, key="sql_numeric_measure")
            fig = px.histogram(result, x=measure, nbins=30, title=f"Distribution of {measure.replace('_', ' ')} · {label}")
            show_chart(st, fig)
        else:
            st.info("This result has no numeric measure or suitable grouping field to chart. Use the table and full CSV instead.")
        return

    if not dimensions:
        return
    controls = st.columns([1.2, 1.2, 1])
    group = controls[0].selectbox("Group results by", dimensions, key="sql_chart_group")
    measure_options = ["Record count"] + numeric
    grouped_result = len(result) <= 15 and cardinality.loc[dimensions].max() == len(result)
    measure_default = 1 if grouped_result and numeric else 0
    measure = controls[1].selectbox("Measure", measure_options, index=measure_default, key="sql_chart_measure")
    if measure == "Record count":
        grouped = result.groupby(group, dropna=False).size().rename("Records").reset_index()
        value_column = "Records"
    else:
        aggregation = controls[2].selectbox("Summarize", ["Sum", "Average", "Median"], key="sql_chart_aggregation")
        operation = {"Sum": "sum", "Average": "mean", "Median": "median"}[aggregation]
        grouped = result.groupby(group, dropna=False)[measure].agg(operation).reset_index()
        value_column = measure

    options = ["Bar"]
    if len(grouped) <= 10 and (grouped[value_column] >= 0).all() and grouped[value_column].sum() > 0:
        options.append("Donut")
    if pd.api.types.is_numeric_dtype(grouped[group]):
        options.append("Line")
    chart_type = controls[2].selectbox("View", options, key="sql_chart_type") if measure == "Record count" else st.selectbox("View", options, key="sql_chart_type")

    if len(grouped) > 15:
        grouped = grouped.nlargest(15, value_column).sort_values(value_column)
        st.caption("The chart shows the 15 largest groups. The result count, preview and CSV use the complete query result.")
    measure_title = value_column.replace("_", " ").title()
    title = f"{aggregation + ' ' if measure != 'Record count' else ''}{measure_title} by {group.replace('_', ' ').title()}"
    if chart_type == "Donut":
        fig = px.pie(grouped, names=group, values=value_column, hole=.58, title=title)
    elif chart_type == "Line":
        fig = px.line(grouped.sort_values(group), x=group, y=value_column, markers=True, title=title)
    else:
        fig = px.bar(grouped.sort_values(value_column), x=value_column, y=group, orientation="h", color=value_column, title=title)
    show_chart(st, fig)


def _visualize(result, label, df, fields):
    fig, insight = _business_chart(result, label, df, fields)
    if fig is None:
        _visualize_custom(result, label)
        return
    show_chart(st, fig, insight=insight, key="sql_business_question_chart")
    with st.expander("Build another view from this result"):
        _visualize_custom(result, label)


def _show_result(result, label, truncated, df, fields):
    status = f"{label} · {len(result):,} rows returned"
    status += f" · capped at {MAX_ROWS:,} rows" if truncated else " · complete result"
    st.success(status)
    summary = _question_metrics(result, label, df, fields)
    with st.container(border=True):
        st.markdown("#### Question-specific KPIs")
        metrics = st.columns(min(4, max(1, len(summary))))
        for column, (name, value) in zip(metrics, summary):
            column.metric(name, value)

    if len(result):
        numeric = list(result.select_dtypes(include="number").columns)
        if numeric and len(result) == 1:
            value = result.iloc[0][numeric[0]]
            takeaway = f"The SQL aggregate returned {numeric[0].replace('_', ' ').title()}: {_format_number(value)}."
        elif numeric:
            values = pd.to_numeric(result[numeric[0]], errors="coerce").dropna()
            takeaway = (
                f"The complete result contains {len(result):,} rows. {numeric[0].replace('_', ' ').title()} "
                f"ranges from {values.min():,.2f} to {values.max():,.2f}. Group the results below to compare categories."
            ) if len(values) else f"The complete SQL result contains {len(result):,} rows across {len(result.columns)} fields."
        else:
            takeaway = f"The complete SQL result contains {len(result):,} rows across {len(result.columns)} fields."
        show_insight(st, takeaway)

    if truncated:
        st.warning(f"This custom query exceeded the {MAX_ROWS:,}-row safety limit. The preview, chart and CSV use the returned rows only.")
    visual_tab, table_tab = st.tabs(["Explore results", "Result table"])
    with visual_tab:
        _visualize(result, label, df, fields)
    with table_tab:
        preview = result.head(PREVIEW_ROWS)
        show_table(
            st, preview, "Executed query preview",
            insight=f"Showing the first {len(preview):,} of {len(result):,} rows. The chart uses the full result; CSV download includes the full result.",
            hide_index=True, height=480,
        )
        st.download_button("Download full result CSV", result.to_csv(index=False).encode("utf-8"), "ola_sql_result.csv", "text/csv")


def _sidebar_context(metrics, label, truncated):
    description = f"Executed {label}. " + "; ".join(f"{name}: {value}" for name, value in metrics[:2])
    description += f" Capped at {MAX_ROWS:,} rows." if truncated else " Full result returned."
    set_sidebar_context("SQL explorer", description, metrics[:3])


def render(df, fields):
    st.markdown("### Business questions")
    st.caption("Choose a numbered business question or write a custom query. Selecting a question and editing SQL do not run it.")
    first = next(iter(LABELS))
    st.session_state.setdefault("sql_question", first)
    st.session_state.setdefault("sql_editor", QUESTIONS[LABELS[first]][0])
    st.selectbox("Choose a numbered question", [*LABELS, CUSTOM], key="sql_question", on_change=_question_changed)
    selected = st.session_state["sql_question"]
    label = CUSTOM if selected == CUSTOM else LABELS[selected]
    st.caption(
        "One read-only SELECT or WITH statement against `bookings`. Writes, schema changes and other tables are blocked."
        if selected == CUSTOM else QUESTIONS[label][1]
    )
    with st.expander("Available SQL fields", expanded=False):
        schema = pd.DataFrame({"SQL field": list(COLUMN_MAP.values())})
        st.dataframe(schema, hide_index=True, width="stretch")
        st.caption("Processed feature fields are also available using their displayed names in double quotes, for example `\"Booking Hour\"`.")

    with st.form("sql_execution_form", clear_on_submit=False):
        st.text_area("SQL query", key="sql_editor", height=190, help="This query runs only after you click Run SQL Query.")
        execute = st.form_submit_button("Run SQL Query", type="primary", width="stretch")

    if execute:
        query = st.session_state["sql_editor"]
        execution_label = _executed_label(query, selected, label)
        try:
            result, truncated = execute_readonly_query(query, df)
            for key in ("sql_chart_group", "sql_chart_measure", "sql_chart_type", "sql_chart_aggregation", "sql_numeric_measure"):
                st.session_state.pop(key, None)
            st.session_state["sql_last_result"] = result
            st.session_state["sql_last_query"] = query
            st.session_state["sql_last_error"] = None
            st.session_state["sql_last_truncated"] = truncated
            st.session_state["sql_last_question_label"] = execution_label
        except Exception as exc:
            st.session_state["sql_last_error"] = str(exc)
            st.session_state.pop("sql_last_result", None)
            st.session_state["sql_last_query"] = query
            st.session_state["sql_last_question_label"] = execution_label
            set_sidebar_context("SQL explorer", f"{execution_label} failed: {exc}", [("Query", execution_label), ("Execution", "Failed"), ("Access", "Read only")])

    error = st.session_state.get("sql_last_error")
    if error:
        st.error(error)
        with st.expander("Submitted SQL"):
            st.code(st.session_state.get("sql_last_query", ""), language="sql")
    elif "sql_last_result" in st.session_state:
        result = st.session_state["sql_last_result"]
        executed_label = st.session_state.get("sql_last_question_label", label)
        summary = _question_metrics(result, executed_label, df, fields)
        with st.expander("Executed SQL", expanded=False):
            st.code(st.session_state.get("sql_last_query", ""), language="sql")
        _show_result(result, executed_label, st.session_state.get("sql_last_truncated", False), df, fields)
        _sidebar_context(summary, executed_label, st.session_state.get("sql_last_truncated", False))
    else:
        st.info("Ready when you are. Review the SQL, then click **Run SQL Query** to execute it.")
        set_sidebar_context("SQL explorer", f"Selected: {label}. No query has been executed yet.", [("Selected question", label), ("Execution", "Waiting"), ("Access", "Read only")])
