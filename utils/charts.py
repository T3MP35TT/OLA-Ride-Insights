"""Shared OLA chart styling, chart insights, and table cards."""
import html
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

COLORS = ["#7D9400", "#171717", "#D7DF23", "#66705D", "#E89E25", "#AAB1A1", "#D46A42"]
TEMPLATE = "plotly_white"
px.defaults.color_discrete_sequence = COLORS
px.defaults.color_continuous_scale = ["#F3F5C7", "#D7DF23", "#9EB300", "#526800"]
px.defaults.template = TEMPLATE


def brand_figure(fig, title: str | None = None):
    fig.update_layout(
        template=TEMPLATE, colorway=COLORS, title=title or fig.layout.title.text,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": "#27291E", "size": 13},
        margin={"l": 28, "r": 28, "t": 45, "b": 35}, legend_title_text="",
        hoverlabel={"bgcolor": "#202217", "font": {"color": "white", "size": 12}},
        hovermode="closest", autosize=True, height=430,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont={"color": "#62664C"}, title_font={"color": "#373A2C"})
    fig.update_yaxes(gridcolor="#E6E9D4", gridwidth=1, zeroline=False, tickfont={"color": "#62664C"}, title_font={"color": "#373A2C"})
    return fig


def show_insight(st, message, label="KEY INSIGHT"):
    st.markdown(
        f"<div class='ola-key-insight'><span>{html.escape(str(label))}</span>"
        f"<div>{html.escape(str(message))}</div></div>",
        unsafe_allow_html=True,
    )


def _list(values):
    if values is None:
        return []
    try:
        return list(values)
    except TypeError:
        return [values]


def chart_insight(fig, title):
    """Create a concise descriptive takeaway from the chart's plotted values."""
    for trace in fig.data:
        kind = str(getattr(trace, "type", ""))
        if kind == "pie":
            labels = _list(getattr(trace, "labels", None))
            values = pd.to_numeric(pd.Series(_list(getattr(trace, "values", None))), errors="coerce")
            if labels and len(labels) == len(values) and values.notna().any():
                idx = int(values.fillna(-np.inf).values.argmax())
                share = values.iloc[idx] / values.sum() * 100 if values.sum() else 0
                return f"{labels[idx]} is the largest segment ({share:.1f}% of the displayed total)."

        if kind == "histogram":
            raw = pd.to_numeric(pd.Series(_list(getattr(trace, "x", None))), errors="coerce").dropna()
            if len(raw):
                return f"The median is {raw.median():,.2f}; the middle half of displayed values spans {raw.quantile(.25):,.2f}–{raw.quantile(.75):,.2f}."

        if kind == "bar":
            xs, ys = _list(getattr(trace, "x", None)), _list(getattr(trace, "y", None))
            xnum = pd.to_numeric(pd.Series(xs), errors="coerce") if xs else pd.Series(dtype=float)
            ynum = pd.to_numeric(pd.Series(ys), errors="coerce") if ys else pd.Series(dtype=float)
            if len(xs) == len(ys) and len(xs):
                if xnum.notna().all() and not ynum.notna().all():
                    values, labels = xnum, ys
                elif ynum.notna().all() and not xnum.notna().all():
                    values, labels = ynum, xs
                else:
                    continue
                idx = int(values.values.argmax())
                return f"{labels[idx]} leads this comparison with {values.iloc[idx]:,.2f}."

        if kind in {"box", "violin"}:
            xs = _list(getattr(trace, "x", None))
            ys = pd.to_numeric(pd.Series(_list(getattr(trace, "y", None))), errors="coerce")
            if len(xs) == len(ys) and len(xs):
                grouped = pd.DataFrame({"group": xs, "value": ys}).dropna().groupby("group")["value"].median().sort_values(ascending=False)
                if len(grouped):
                    return f"{grouped.index[0]} has the highest median ({grouped.iloc[0]:,.2f}); medians are descriptive and do not explain the cause."
            ys = ys.dropna()
            if len(ys):
                return f"The median value is {ys.median():,.2f}, with an interquartile range of {ys.quantile(.25):,.2f}–{ys.quantile(.75):,.2f}."

        if kind in {"heatmap", "histogram2d"}:
            z = np.asarray(getattr(trace, "z", []), dtype=float)
            if z.size and np.isfinite(z).any():
                row, col = np.unravel_index(np.nanargmax(z), z.shape)
                xs, ys = _list(getattr(trace, "x", None)), _list(getattr(trace, "y", None))
                x = xs[col] if len(xs) > col else f"column {col + 1}"
                y = ys[row] if len(ys) > row else f"row {row + 1}"
                return f"The strongest concentration is {y} × {x} ({z[row, col]:,.0f} observations)."

        if kind in {"scatter", "scattergl"} and "lines" in str(getattr(trace, "mode", "")):
            ys = pd.to_numeric(pd.Series(_list(getattr(trace, "y", None))), errors="coerce").dropna()
            if len(ys) > 1:
                change = ys.iloc[-1] - ys.iloc[0]
                trend = "increased" if change > 0 else "decreased" if change < 0 else "ended near its start"
                return f"{getattr(trace, 'name', 'The series')} {trend} by {abs(change):,.2f} from first to last point."

        if kind in {"scatter", "scattergl"}:
            xs = pd.to_numeric(pd.Series(_list(getattr(trace, "x", None))), errors="coerce")
            ys = pd.to_numeric(pd.Series(_list(getattr(trace, "y", None))), errors="coerce")
            paired = pd.concat([xs.rename("x"), ys.rename("y")], axis=1).dropna()
            if len(paired) > 2:
                corr = paired.x.corr(paired.y)
                direction = "positive" if corr > 0 else "negative" if corr < 0 else "no linear"
                return f"The plotted measures have a {direction} association (r={corr:.2f}) over {len(paired):,} points; this is not evidence of causation."
            if len(ys.dropna()):
                return f"{getattr(trace, 'name', 'This series')} reaches {ys.max():,.2f} on the vertical measure. Compare the point labels and hover details."

    return f"This view compares the plotted values for {title}. Use the filters and hover details to inspect differences across the displayed groups."


def table_insight(frame):
    if frame.empty:
        return "No records match the current table selection."
    numeric = list(frame.select_dtypes(include="number").columns)
    dimensions = [col for col in frame.columns if col not in numeric]
    for measure in numeric:
        values = pd.to_numeric(frame[measure], errors="coerce")
        if values.notna().any():
            idx = values.idxmax()
            if dimensions:
                return f"Highest {measure.replace('_', ' ').lower()}: {frame.loc[idx, dimensions[0]]} ({values.loc[idx]:,.2f}) among {len(frame):,} displayed rows."
            return f"{measure.replace('_', ' ').title()} ranges from {values.min():,.2f} to {values.max():,.2f} across {len(frame):,} displayed rows."
    missing = int(frame.isna().sum().sum())
    return f"The table contains {len(frame):,} rows and {frame.shape[1]} fields; {missing:,} displayed cells are missing."


def show_table(st, frame, title="Data table", insight=None, **kwargs):
    with st.container(border=True):
        st.markdown(f"<div class='ola-chart-title'>{html.escape(title)}</div>", unsafe_allow_html=True)
        st.dataframe(frame, width="stretch", **kwargs)
        show_insight(st, insight or table_insight(frame))


def show_chart(st, fig, title=None, insight=None, key=None):
    chart_title = title or fig.layout.title.text or "Analysis"
    takeaway = insight or chart_insight(fig, chart_title)
    fig.update_layout(title=None)
    with st.container(border=True):
        st.markdown(f"<div class='ola-chart-title'>{html.escape(str(chart_title))}</div>", unsafe_allow_html=True)
        st.plotly_chart(brand_figure(fig), width="stretch", key=key, config={"displaylogo": False, "responsive": True})
        show_insight(st, takeaway)
