"""DateTime card rendering functionality."""

from typing import Optional

import numpy as np

try:  # optional
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

from .card_base import CardRenderer, QualityAssessor, TableBuilder
from .card_config import DEFAULT_CHART_DIMS, DEFAULT_DT_CONFIG
from .card_types import DateTimeStats, QualityFlags
from .svg_utils import nice_ticks as _nice_ticks


class DateTimeCardRenderer(CardRenderer):
    """Renders datetime data cards."""

    def __init__(self):
        super().__init__()
        self.quality_assessor = QualityAssessor()
        self.table_builder = TableBuilder()
        self.dt_config = DEFAULT_DT_CONFIG
        self.chart_dims = DEFAULT_CHART_DIMS

    def _get_chart_dimensions(self) -> tuple[int, int]:
        """Get consistent chart dimensions for datetime timeline."""
        return self.chart_dims.width, self.chart_dims.height + 20

    def render_card(self, stats: DateTimeStats) -> str:
        """Render a complete datetime card."""
        col_id = self.safe_col_id(stats.name)
        safe_name = self.safe_html_escape(stats.name)

        # Calculate percentages and quality flags
        total = int(getattr(stats, "count", 0) + getattr(stats, "missing", 0))
        miss_pct = (stats.missing / max(1, total)) * 100.0
        miss_cls = "crit" if miss_pct > 20 else ("warn" if miss_pct > 0 else "")

        quality_flags = self.quality_assessor.assess_datetime_quality(stats)
        quality_flags_html = self._build_quality_flags_html(
            quality_flags, stats, miss_pct
        )

        # Build components
        left_table = self._build_left_table(stats, miss_cls, miss_pct)
        right_table = self._build_right_table(stats)

        # Chart
        chart_html = self._build_timeline_chart(stats)

        # Details
        details_html = self._build_details_section(col_id, stats)

        return self._assemble_card(
            col_id,
            safe_name,
            stats,
            quality_flags_html,
            left_table,
            right_table,
            chart_html,
            details_html,
        )

    def _build_quality_flags_html(
        self, flags: QualityFlags, stats: DateTimeStats, miss_pct: float
    ) -> str:
        """Build quality flags HTML for datetime data with enhanced insights."""
        flag_items = []

        if flags.missing:
            severity = "bad" if miss_pct > 20 else "warn"
            flag_items.append(f'<li class="flag {severity}">Missing</li>')

        if flags.monotonic_increasing:
            flag_items.append('<li class="flag good">Monotonic ↑</li>')

        if flags.monotonic_decreasing:
            flag_items.append('<li class="flag good">Monotonic ↓</li>')

        # Weekend concentrated
        weekend_ratio = getattr(stats, "weekend_ratio", 0.0)
        if weekend_ratio > 0.35:  # >35% on weekends (expected ~28.5%)
            flag_items.append('<li class="flag">Weekend-heavy</li>')

        # Business hours concentrated
        business_hours = getattr(stats, "business_hours_ratio", 0.0)
        if business_hours > 0.5:  # >50% during business hours
            flag_items.append('<li class="flag good">Business hours</li>')

        # Seasonal pattern detected
        seasonal = getattr(stats, "seasonal_pattern", None)
        if seasonal:
            flag_items.append(f'<li class="flag">Peak in {seasonal}</li>')

        # High uniqueness (like IDs or log timestamps)
        unique_est = getattr(stats, "unique_est", 0)
        total = stats.count + stats.missing
        if total > 0 and (unique_est / total) > 0.95:
            flag_items.append('<li class="flag warn">High uniqueness</li>')

        # Irregular intervals (high std dev)
        avg_interval = getattr(stats, "avg_interval_seconds", 0.0)
        interval_std = getattr(stats, "interval_std_seconds", 0.0)
        if avg_interval > 0 and (interval_std / avg_interval) > 2.0:
            flag_items.append('<li class="flag warn">Irregular intervals</li>')

        return (
            f'<ul class="quality-flags">{"".join(flag_items)}</ul>'
            if flag_items
            else ""
        )

    def _build_left_table(
        self, stats: DateTimeStats, miss_cls: str, miss_pct: float
    ) -> str:
        """Build left statistics table."""
        # Format time span
        time_span = getattr(stats, "time_span_days", 0.0)
        if time_span >= 365:
            span_display = f"{time_span / 365:.1f} years"
        elif time_span >= 30:
            span_display = f"{time_span / 30:.1f} months"
        else:
            span_display = f"{time_span:.1f} days"

        # Format avg interval
        avg_interval = getattr(stats, "avg_interval_seconds", 0.0)
        if avg_interval >= 86400:
            interval_display = f"{avg_interval / 86400:.1f} days"
        elif avg_interval >= 3600:
            interval_display = f"{avg_interval / 3600:.1f} hours"
        elif avg_interval >= 60:
            interval_display = f"{avg_interval / 60:.1f} minutes"
        else:
            interval_display = f"{avg_interval:.1f} seconds"

        # Format interval std in human-readable way
        interval_std = getattr(stats, "interval_std_seconds", 0.0)
        if interval_std >= 86400:
            std_display = f"{interval_std / 86400:.1f} days"
        elif interval_std >= 3600:
            std_display = f"{interval_std / 3600:.1f} hours"
        elif interval_std >= 60:
            std_display = f"{interval_std / 60:.1f} minutes"
        else:
            std_display = f"{interval_std:.1f} seconds"

        data = [
            ("Count", f"{int(getattr(stats, 'count', 0)):,}", "num"),
            ("Unique", f"{int(getattr(stats, 'unique_est', 0)):,} (≈)", "num"),
            (
                "Missing",
                f"{int(getattr(stats, 'missing', 0)):,} ({miss_pct:.1f}%)",
                f"num {miss_cls}",
            ),
            ("Timezone", "UTC", None),
            ("Time span", span_display, None),
            ("Avg interval", interval_display, None),
            ("Interval std", std_display, None),
        ]

        return self.table_builder.build_key_value_table(data)

    def _build_right_table(self, stats: DateTimeStats) -> str:
        """Build right statistics table with temporal analysis."""
        mem_display = self.format_bytes(int(getattr(stats, "mem_bytes", 0))) + " (≈)"

        # Seasonal pattern removed from display

        # Calculate data density (records per day)
        time_span_days = getattr(stats, "time_span_days", 0.0)
        count = getattr(stats, "count", 0)
        if time_span_days > 0:
            density = count / time_span_days
            if density >= 1:
                density_display = f"{density:.1f} records/day"
            else:
                density_display = f"{1 / density:.1f} days/record"
        else:
            density_display = "—"

        data = [
            (
                "Min",
                self._format_timestamp(getattr(stats, "min_ts", None)),
                "timestamp-value",
            ),
            (
                "Max",
                self._format_timestamp(getattr(stats, "max_ts", None)),
                "timestamp-value",
            ),
            ("Weekend %", f"{getattr(stats, 'weekend_ratio', 0.0) * 100:.1f}%", "num"),
            (
                "Business hrs %",
                f"{getattr(stats, 'business_hours_ratio', 0.0) * 100:.1f}%",
                "num",
            ),
            ("Data density", density_display, None),
            ("Processed bytes", mem_display, "num"),
        ]

        return self.table_builder.build_key_value_table(data)

    def _format_timestamp(self, ts: Optional[int]) -> str:
        """Format a UTC nanoseconds epoch as ISO8601 Z; fallback safely."""
        if ts is None:
            return "—"
        try:
            # Prefer pandas if available for robustness
            if pd is not None:  # type: ignore
                dt = pd.to_datetime(int(ts), utc=True)
                formatted = dt.isoformat()
                return formatted
        except Exception:
            pass
        try:
            from datetime import datetime as _dt

            formatted = _dt.utcfromtimestamp(int(ts) / 1_000_000_000).isoformat() + "Z"
            return formatted
        except Exception:
            return str(ts)

    def _build_sparkline(self, counts: list[int]) -> str:
        """Return an 8-level unicode block sparkline for small arrays."""
        if not counts:
            return ""
        m = max(counts) or 1
        blocks = "▁▂▃▄▅▆▇█"
        return "".join(
            blocks[min(len(blocks) - 1, int(c * (len(blocks) - 1) / m))] for c in counts
        )

    def _build_timeline_chart(self, stats: DateTimeStats) -> str:
        """Build timeline chart."""
        sample = getattr(stats, "sample_ts", None)
        tmin = getattr(stats, "min_ts", None)
        tmax = getattr(stats, "max_ts", None)
        scale_count = getattr(stats, "sample_scale", 1.0)

        svg = self._build_timeline_svg(
            sample,
            tmin,
            tmax,
            stats.name,
            bins=self.dt_config.default_bins,
            scale_count=scale_count,
        )

        return f"""
        <div class="timeline-chart">
            {svg}
        </div>
        """

    def _build_timeline_svg(
        self,
        sample: Optional[list[int]],
        tmin: Optional[int],
        tmax: Optional[int],
        column_name: str,
        *,
        bins: int = 60,
        scale_count: float = 1.0,
    ) -> str:
        """Build timeline SVG from raw ns samples."""
        if not sample or tmin is None or tmax is None:
            width, height = self._get_chart_dimensions()
            return self.create_empty_svg("dt-svg", width, height)

        try:
            a = np.asarray(sample, dtype=np.int64)
            if a.size == 0:
                width, height = self._get_chart_dimensions()
                return self.create_empty_svg("dt-svg", width, height)

            if tmin == tmax:
                tmax = tmin + 1

            counts, edges = np.histogram(
                a, bins=int(max(10, min(bins, 180))), range=(int(tmin), int(tmax))
            )
            counts = np.maximum(
                0, np.round(counts * max(1.0, float(scale_count)))
            ).astype(int)
            y_max = int(max(1, counts.max()))

            width, height = self._get_chart_dimensions()
            margin_left, margin_right, margin_top, margin_bottom = 45, 35, 25, 42
            iw = width - margin_left - margin_right
            ih = height - margin_top - margin_bottom

            def sx(x):
                return margin_left + (x - tmin) / (tmax - tmin) * iw

            def sy(y):
                return margin_top + (1 - y / y_max) * ih

            centers = (edges[:-1] + edges[1:]) / 2.0
            pts = " ".join(
                f"{sx(x):.2f},{sy(float(c)):.2f}" for x, c in zip(centers, counts)
            )
            y_ticks, _ = _nice_ticks(0, y_max, 5)

            n_xt = 5
            xt_vals = np.linspace(tmin, tmax, n_xt)
            span_ns = tmax - tmin

            def _format_xtick(v):
                try:
                    if pd is not None:  # type: ignore
                        ts = pd.to_datetime(int(v), utc=True)
                        if span_ns <= self.dt_config.short_span_ns:
                            return ts.strftime("%Y-%m-%d %H:%M")
                        return ts.date().isoformat()
                except Exception:
                    pass
                try:
                    from datetime import datetime as _dt

                    return _dt.utcfromtimestamp(int(v) / 1_000_000_000).strftime(
                        "%Y-%m-%d"
                    )
                except Exception:
                    return str(v)

            parts = [
                f'<svg class="dt-svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Timeline">',
            ]

            # Add title with error handling
            try:
                title_text = self.safe_html_escape(column_name)
                parts.append(
                    f'<text x="{width // 2}" y="15" '
                    f'text-anchor="middle" class="hist-title" '
                    f'font-family="system-ui, -apple-system, sans-serif" '
                    f'font-size="12">{title_text}</text>'
                )
            except Exception:
                # Fallback to generic title
                parts.append(
                    f'<text x="{width // 2}" y="15" '
                    f'text-anchor="middle" class="hist-title" '
                    f'font-family="system-ui, -apple-system, sans-serif" '
                    f'font-size="12">Timeline</text>'
                )

            parts.append('<g class="plot-area">')

            # Grid lines
            for yt in y_ticks:
                parts.append(
                    f'<line class="grid" x1="{margin_left}" y1="{sy(yt):.2f}" x2="{margin_left + iw}" y2="{sy(yt):.2f}"></line>'
                )

            # Main line
            parts.append(f'<polyline class="line" points="{pts}"></polyline>')

            # Hotspots for tooltips
            parts.append('<g class="hotspots">')
            for i, c in enumerate(counts):
                if not np.isfinite(c):
                    continue
                x0p = sx(edges[i])
                x1p = sx(edges[i + 1])
                wp = max(1.0, x1p - x0p)
                start_label = _format_xtick(edges[i])
                end_label = _format_xtick(edges[i + 1])
                range_label = (
                    f"{start_label} – {end_label}"
                    if start_label != end_label
                    else start_label
                )
                pct = (c / sum(counts) * 100) if sum(counts) > 0 else 0
                parts.append(
                    f'<rect class="hot" x="{x0p:.2f}" y="{margin_top}" width="{wp:.2f}" height="{ih:.2f}" '
                    f'fill="transparent" pointer-events="all" '
                    f'data-count="{int(c)}" data-pct="{pct:.1f}" data-label="{range_label}">'
                    f"</rect>"
                )
            parts.append("</g>")
            parts.append("</g>")

            # Axes
            x_axis_y = margin_top + ih
            parts.append(
                f'<line class="axis" x1="{margin_left}" y1="{x_axis_y}" x2="{margin_left + iw}" y2="{x_axis_y}"></line>'
            )
            parts.append(
                f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{x_axis_y}"></line>'
            )

            # Y ticks
            for yt in y_ticks:
                py = sy(yt)
                parts.append(
                    f'<line class="tick" x1="{margin_left - 4}" y1="{py:.2f}" x2="{margin_left}" y2="{py:.2f}"></line>'
                )
                lab = int(round(yt))
                parts.append(
                    f'<text class="tick-label" x="{margin_left - 6}" y="{py + 3:.2f}" text-anchor="end">{lab}</text>'
                )

            # X ticks
            for xv in xt_vals:
                px = sx(xv)
                parts.append(
                    f'<line class="tick" x1="{px:.2f}" y1="{x_axis_y}" x2="{px:.2f}" y2="{x_axis_y + 4}"></line>'
                )
                parts.append(
                    f'<text class="tick-label x-tick-label" x="{px:.2f}" y="{x_axis_y + 16:.2f}" text-anchor="middle">{_format_xtick(xv)}</text>'
                )

            # Axis titles removed

            parts.append("</svg>")
            return "".join(parts)
        except Exception:
            width, height = self._get_chart_dimensions()
            return self.create_empty_svg("dt-svg", width, height)

    def _build_temporal_statistics_table(self, stats: DateTimeStats) -> str:
        """Build temporal statistics table with human-readable formatting."""
        # Format time span in human-readable way
        time_span = getattr(stats, "time_span_days", 0.0)
        if time_span >= 365:
            time_span_display = f"{time_span / 365:.1f} years"
        elif time_span >= 30:
            time_span_display = f"{time_span / 30:.1f} months"
        elif time_span >= 7:
            time_span_display = f"{time_span / 7:.1f} weeks"
        else:
            time_span_display = f"{time_span:.1f} days"

        # Format average interval in human-readable way
        avg_interval = getattr(stats, "avg_interval_seconds", 0.0)
        if avg_interval >= 86400:
            interval_display = f"{avg_interval / 86400:.1f} days"
        elif avg_interval >= 3600:
            interval_display = f"{avg_interval / 3600:.1f} hours"
        elif avg_interval >= 60:
            interval_display = f"{avg_interval / 60:.1f} minutes"
        else:
            interval_display = f"{avg_interval:.1f} seconds"

        # Format interval std in human-readable way
        interval_std = getattr(stats, "interval_std_seconds", 0.0)
        if interval_std >= 86400:
            std_display = f"{interval_std / 86400:.1f} days"
        elif interval_std >= 3600:
            std_display = f"{interval_std / 3600:.1f} hours"
        elif interval_std >= 60:
            std_display = f"{interval_std / 60:.1f} minutes"
        else:
            std_display = f"{interval_std:.1f} seconds"

        weekend_ratio = getattr(stats, "weekend_ratio", 0.0)
        business_hours = getattr(stats, "business_hours_ratio", 0.0)
        seasonal = getattr(stats, "seasonal_pattern", None)

        # Table 1: Timestamp details and basic statistics
        timestamp_data = [
            (
                "Min timestamp",
                self._format_timestamp(getattr(stats, "min_ts", None)),
                "timestamp-value",
            ),
            (
                "Max timestamp",
                self._format_timestamp(getattr(stats, "max_ts", None)),
                "timestamp-value",
            ),
            (
                "Unique timestamps",
                f"{int(getattr(stats, 'unique_est', 0)):,} (≈)",
                "num",
            ),
            ("Timezone", "UTC", None),
            ("Time span", time_span_display, None),
            ("Avg interval", interval_display, None),
            ("Interval std dev", std_display, None),
        ]

        # Table 2: Temporal patterns and peaks
        pattern_data = [
            ("Weekend ratio", f"{weekend_ratio * 100:.1f}%", "num"),
            ("Business hours", f"{business_hours * 100:.1f}%", "num"),
            ("Seasonal pattern", seasonal if seasonal else "—", None),
            ("Peak hour", f"{self._get_peak_hour(stats)}", None),
            ("Peak day", f"{self._get_peak_day(stats)}", None),
            ("Peak month", f"{self._get_peak_month(stats)}", None),
            ("Peak year", f"{self._get_peak_year(stats)}", None),
        ]

        # Build both tables
        table1 = self.table_builder.build_key_value_table(timestamp_data)
        table2 = self.table_builder.build_key_value_table(pattern_data)

        return f"""
        <div class="temporal-analysis">
            <div class="temporal-section">
                {table1}
                    </div>
            <div class="temporal-section">
                {table2}
            </div>
        </div>
        """

    def _get_peak_hour(self, stats: DateTimeStats) -> str:
        """Get peak hour from by_hour distribution."""
        by_hour = getattr(stats, "by_hour", []) or []
        if not by_hour or max(by_hour) == 0:
            return "—"
        peak_idx = by_hour.index(max(by_hour))
        return f"{peak_idx:02d}:00 ({by_hour[peak_idx]:,} records)"

    def _get_peak_day(self, stats: DateTimeStats) -> str:
        """Get peak day of week."""
        by_dow = getattr(stats, "by_dow", []) or []
        if not by_dow or max(by_dow) == 0:
            return "—"
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        peak_idx = by_dow.index(max(by_dow))
        return f"{days[peak_idx]} ({by_dow[peak_idx]:,} records)"

    def _get_peak_month(self, stats: DateTimeStats) -> str:
        """Get peak month."""
        by_month = getattr(stats, "by_month", []) or []
        if not by_month or max(by_month) == 0:
            return "—"
        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        peak_idx = by_month.index(max(by_month))
        return f"{months[peak_idx]} ({by_month[peak_idx]:,} records)"

    def _get_peak_year(self, stats: DateTimeStats) -> str:
        """Get peak year."""
        by_year = getattr(stats, "by_year", {}) or {}
        if not by_year or max(by_year.values()) == 0:
            return "—"
        peak_year = max(by_year, key=by_year.get)
        return f"{peak_year} ({by_year[peak_year]:,} records)"

    def _build_missing_values_table(self, stats: DateTimeStats) -> str:
        """Build comprehensive missing values analysis table."""
        # Calculate missing data statistics
        total_values = stats.count + stats.missing
        missing_pct = (
            (stats.missing / max(1, total_values)) * 100.0 if total_values > 0 else 0.0
        )
        present_pct = (
            (stats.count / max(1, total_values)) * 100.0 if total_values > 0 else 0.0
        )

        # Determine severity
        quality_severity, quality_label, quality_icon = self._get_missing_data_severity(
            missing_pct
        )

        # Build summary header
        summary_html = f"""
        <div class="missing-summary">
            <div class="summary-header">
                <span class="icon">📊</span>
                <span class="title">Missing Values Analysis</span>
                <span class="quality-indicator {quality_severity}">
                    {quality_icon} {quality_label} Missing Data
                </span>
            </div>
            <div class="data-overview">
                <div class="overview-item">
                    <span class="label">Total Values</span>
                    <span class="value">{total_values:,}</span>
                </div>
                <div class="overview-item present">
                    <span class="label">Present</span>
                    <span class="value">{stats.count:,}</span>
                    <span class="percentage">({present_pct:.1f}%)</span>
                </div>
                <div class="overview-item missing">
                    <span class="label">Missing</span>
                    <span class="value">{stats.missing:,}</span>
                    <span class="percentage">({missing_pct:.1f}%)</span>
                </div>
            </div>
        </div>
        """

        # Build progress visualization
        progress_html = f"""
        <div class="missing-visualization">
            <div class="progress-container">
                <div class="progress-bar-container">
                    <div class="progress-label">Data Completeness</div>
                    <div class="progress-bar">
                        <div class="progress-fill present" style="width: {present_pct:.1f}%"></div>
                        <div class="progress-fill missing" style="width: {missing_pct:.1f}%"></div>
                    </div>
                    <div class="progress-legend">
                        <span class="legend-item present">Present: {present_pct:.1f}%</span>
                        <span class="legend-item missing">Missing: {missing_pct:.1f}%</span>
                    </div>
                </div>
            </div>
        </div>
        """

        # Add DataPrep-style spectrum visualization
        chunk_visualization_html = self._build_dataprep_spectrum_visualization(stats)

        return summary_html + progress_html + chunk_visualization_html

    def _get_missing_data_severity(self, missing_pct: float) -> tuple[str, str, str]:
        """Get missing data severity classification."""
        if missing_pct >= 50:
            return "critical", "Critical", "🚨"
        elif missing_pct >= 20:
            return "high", "High", "⚠️"
        elif missing_pct >= 5:
            return "medium", "Medium", "⚡"
        else:
            return "low", "Low", "✅"

    def _build_dataprep_spectrum_visualization(self, stats: DateTimeStats) -> str:
        """Build DataPrep-style spectrum visualization for missing values per chunk."""
        # Check if we have chunk metadata
        chunk_metadata = getattr(stats, "chunk_metadata", None)
        if not chunk_metadata:
            return ""

        total_values = stats.count + stats.missing
        if total_values == 0:
            return ""

        # Build the spectrum bar segments
        segments_html = ""

        for start_row, end_row, missing_count in chunk_metadata:
            chunk_size = end_row - start_row + 1
            missing_pct = (
                (missing_count / chunk_size) * 100.0 if chunk_size > 0 else 0.0
            )

            # Calculate segment width as percentage of total
            segment_width_pct = (chunk_size / total_values) * 100.0

            # Determine color based on missing percentage
            if missing_pct <= 5:
                color_class = "spectrum-low"
            elif missing_pct <= 20:
                color_class = "spectrum-medium"
            else:
                color_class = "spectrum-high"

            # Create tooltip content
            tooltip_content = (
                f"Rows {start_row:,}-{end_row:,}: "
                f"{missing_count:,} missing ({missing_pct:.1f}%)"
            )

            segments_html += f"""
            <div class="spectrum-segment {color_class}"
                 style="width: {segment_width_pct:.2f}%"
                 title="{tooltip_content}"
                 data-start="{start_row}"
                 data-end="{end_row}"
                 data-missing="{missing_count}"
                 data-missing-pct="{missing_pct:.1f}">
            </div>
            """

        # Build summary statistics
        total_chunks = len(chunk_metadata)
        max_missing_pct = max(
            (missing_count / (end_row - start_row + 1)) * 100.0
            for start_row, end_row, missing_count in chunk_metadata
        )
        avg_missing_pct = (
            sum(
                (missing_count / (end_row - start_row + 1)) * 100.0
                for start_row, end_row, missing_count in chunk_metadata
            )
            / total_chunks
        )

        # Determine overall severity
        if max_missing_pct >= 50:
            severity = "critical"
            severity_icon = "🚨"
        elif max_missing_pct >= 20:
            severity = "high"
            severity_icon = "⚠️"
        elif max_missing_pct >= 5:
            severity = "medium"
            severity_icon = "⚡"
        else:
            severity = "low"
            severity_icon = "✅"

        return f"""
        <div class="dataprep-spectrum">
            <div class="spectrum-header">
                <span class="spectrum-title">Missing Values Distribution</span>
                <span class="spectrum-stats">
                    {total_chunks} chunks • {max_missing_pct:.1f}% max • {avg_missing_pct:.1f}% avg
                </span>
            </div>

            <div class="spectrum-bar">
                {segments_html}
            </div>

            <div class="spectrum-summary">
                <span class="severity-indicator {severity}">
                    {severity_icon} {severity.title()} Missing Data
                </span>
                <span class="spectrum-note">
                    Hover over segments to see chunk details
                </span>
            </div>

            <div class="spectrum-legend">
                <div class="legend-item">
                    <span class="legend-color spectrum-low"></span>
                    <span class="legend-label">Low (0-5%)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color spectrum-medium"></span>
                    <span class="legend-label">Medium (5-20%)</span>
                </div>
                <div class="legend-item">
                    <span class="legend-color spectrum-high"></span>
                    <span class="legend-label">High (20%+)</span>
                </div>
            </div>
        </div>
        """

    def _build_details_section(self, col_id: str, stats: DateTimeStats) -> str:
        """Build details section with multiple tabs."""
        # Build histogram breakdown
        breakdown_html = self._build_breakdown_histograms(col_id, stats)

        # New tables
        stats_table = self._build_temporal_statistics_table(stats)
        missing_table = self._build_missing_values_table(stats)
        return f"""
        <section id="{col_id}-details" class="details-section" hidden>
            <nav class="tabs" role="tablist" aria-label="More details">
                <button role="tab" class="active" data-tab="stats">Statistics</button>
                <button role="tab" data-tab="breakdown">Temporal Distribution</button>
                <button role="tab" data-tab="missing">Missing Values</button>
            </nav>
            <div class="tab-panes">
                <section class="tab-pane active" data-tab="stats">
                    <div class="sub">
                        <div class="hdr">Temporal Analysis</div>
                        {stats_table}
                    </div>
                </section>
                <section class="tab-pane" data-tab="breakdown">
                    {breakdown_html}
                </section>
                <section class="tab-pane" data-tab="missing">
                    <div class="sub"><div class="hdr">Missing Values</div>{missing_table}</div>
                </section>
            </div>
        </section>
        """

    def _build_breakdown_histograms(self, col_id: str, stats: DateTimeStats) -> str:
        """Build histogram containers for hour, DOW, month, and year distributions."""
        import json

        # Prepare data for JavaScript
        hour_counts = getattr(stats, "by_hour", None) or []
        dow_counts = getattr(stats, "by_dow", None) or []
        month_counts = getattr(stats, "by_month", None) or []
        year_data = getattr(stats, "by_year", None) or {}

        # Convert year dict to sorted arrays
        if year_data:
            sorted_years = sorted(year_data.keys())
            year_values = [year_data[y] for y in sorted_years]
            year_labels = sorted_years
        else:
            year_values = []
            year_labels = []

        # Build JSON metadata for JavaScript renderer
        dt_meta = {
            "counts": {
                "hour": hour_counts,
                "dow": dow_counts,
                "month": month_counts,
                "year": {"values": year_values, "labels": year_labels},
            }
        }

        # Build HTML with histogram containers
        return f'''
        <script type="application/json" id="{col_id}-dt-meta">{json.dumps(dt_meta)}</script>
        <div class="dt-breakdown-grid">
            <div class="dt-breakdown-item">
                <h4>Hour of Day</h4>
                <div id="{col_id}-dt-hour" class="dt-chart"></div>
            </div>
            <div class="dt-breakdown-item">
                <h4>Day of Week</h4>
                <div id="{col_id}-dt-dow" class="dt-chart"></div>
            </div>
            <div class="dt-breakdown-item">
                <h4>Month</h4>
                <div id="{col_id}-dt-month" class="dt-chart"></div>
            </div>
            <div class="dt-breakdown-item">
                <h4>Year</h4>
                <div id="{col_id}-dt-year" class="dt-chart"></div>
            </div>
        </div>
        '''

    def _assemble_card(
        self,
        col_id: str,
        safe_name: str,
        stats: DateTimeStats,
        quality_flags_html: str,
        left_table: str,
        right_table: str,
        chart_html: str,
        details_html: str,
    ) -> str:
        """Assemble the complete card HTML."""
        return f"""
        <article class="var-card" id="{col_id}">
            <header class="var-card__header">
                <div class="title">
                    <span class="colname">{safe_name}</span>
                    <span class="badge">Datetime</span>
                    <span class="dtype chip">{stats.dtype_str}</span>
                    {quality_flags_html}
                </div>
            </header>
            <div class="var-card__body">
                <div class="triple-row">
                    <div class="box stats-left">{left_table}</div>
                    <div class="box stats-right">{right_table}</div>
                    <div class="box chart">{chart_html}</div>
                </div>
                <div class="card-controls" role="group" aria-label="Column controls">
                    <div class="details-slot">
                        <button type="button" class="details-toggle btn-soft" aria-controls="{col_id}-details" aria-expanded="false">Details</button>
                    </div>
                    <div class="controls-slot"></div>
                </div>
                {details_html}
            </div>
        </article>
        """
