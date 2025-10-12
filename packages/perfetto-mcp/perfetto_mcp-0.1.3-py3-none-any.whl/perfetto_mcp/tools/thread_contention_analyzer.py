"""Thread contention analyzer using android.monitor_contention module."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .base import BaseTool, ToolError
from ..utils.query_helpers import format_query_result_row

logger = logging.getLogger(__name__)


class ThreadContentionAnalyzerTool(BaseTool):
    """Identify thread contention and synchronization bottlenecks.

    Aggregates monitor contention events (Java synchronized blocks/methods) and
    groups contentions by blocked/blocking thread pairs and methods to compute
    contention statistics and severity. Supports time-scoped analysis,
    minimum-duration filtering, example events, and optional per-thread
    blocked-state breakdown. Provides explicit metadata about analysis source
    and fallbacks used.
    """

    def thread_contention_analyzer(
        self,
        trace_path: str,
        process_name: str,
        time_range: dict | None = None,
        min_block_ms: float = 50.0,
        include_per_thread_breakdown: bool = False,
        include_examples: bool = False,
        limit: int = 80,
    ) -> str:
        """Analyze thread contention for a given process.

        Parameters
        ----------
        trace_path : str
            Path to the Perfetto trace file.
        process_name : str
            Exact process name to analyze.

        Returns
        -------
        str
            JSON envelope with fields: processName, tracePath, success, error, result.
            Result shape:
              {
                totalCount: number,
                contentions: [
                  {
                    blocked_thread_name, blocking_thread_name, short_blocking_method_name,
                    contention_count, total_blocked_ms, avg_blocked_ms, max_blocked_ms,
                    total_waiters, max_concurrent_waiters, severity
                  }
                ],
                filters: { process_name },
                analysisSource: "monitor_contention" | "scheduler_inferred",
                primaryDataUnavailable: bool,
                usesWakerLinkage?: bool,
                usedSchedBlockedReason?: bool,
                fallbackNotice?: str,
                timeRangeMs?: { start_ms, end_ms } | null,
                thresholds?: { min_block_ms },
                dataDependencies?: [str],
                notes?: [str],
                examples?: [...],
                blocked_state_breakdown?: [...],
                top_dstate_functions?: [...]
              }
        """

        def _op(tp):
            if not process_name or not isinstance(process_name, str):
                raise ToolError("INVALID_PARAMETERS", "process_name must be a non-empty string")

            safe_proc = process_name.replace("'", "''")

            # Parse time range
            start_ns = None
            end_ns = None
            notes: List[str] = []
            if time_range and isinstance(time_range, dict):
                try:
                    start_ms = time_range.get("start_ms")
                    end_ms = time_range.get("end_ms")
                    if start_ms is not None and end_ms is not None:
                        start_ns = int(float(start_ms) * 1_000_000)
                        end_ns = int(float(end_ms) * 1_000_000)
                except Exception:
                    notes.append("Invalid time_range provided; ignoring")
                    start_ns = None
                    end_ns = None
            else:
                notes.append("time_range not supplied; scanned whole trace")

            # Thresholds and limits
            min_block_ns = int(float(min_block_ms) * 1_000_000)
            example_limit = int(limit)
            group_limit = int(limit)

            # Build primary (monitor_contention) SQL with filters
            where_clauses = [f"upid = (SELECT upid FROM process WHERE name = '{safe_proc}')"]
            if start_ns is not None and end_ns is not None:
                where_clauses.append(f"(ts + dur >= {start_ns} AND ts <= {end_ns})")
            if min_block_ns > 0:
                where_clauses.append(f"dur >= {min_block_ns}")

            where_sql = " AND ".join(where_clauses)

            primary_sql = f"""
            INCLUDE PERFETTO MODULE android.monitor_contention;

            WITH events AS (
              SELECT *
              FROM android_monitor_contention
              WHERE {where_sql}
            ), agg AS (
              SELECT 
                blocked_thread_name,
                blocking_thread_name,
                short_blocking_method_name,
                COUNT(*) as contention_count,
                SUM(dur) / 1e6 as total_blocked_ms,
                AVG(dur) / 1e6 as avg_blocked_ms,
                MAX(dur) / 1e6 as max_blocked_ms,
                SUM(waiter_count) as total_waiters,
                MAX(blocked_thread_waiter_count) as max_concurrent_waiters
              FROM events
              GROUP BY blocked_thread_name, blocking_thread_name, short_blocking_method_name
            )
            SELECT 
              blocked_thread_name,
              blocking_thread_name,
              short_blocking_method_name,
              contention_count,
              CAST(total_blocked_ms AS REAL) as total_blocked_ms,
              CAST(avg_blocked_ms AS REAL) as avg_blocked_ms,
              CAST(max_blocked_ms AS REAL) as max_blocked_ms,
              total_waiters,
              max_concurrent_waiters
            FROM agg
            ORDER BY total_blocked_ms DESC
            LIMIT {group_limit};
            """

            def _heuristic_is_main(thread_name: str | None) -> bool:
                if not thread_name:
                    return False
                try:
                    return "main" in thread_name.lower()
                except Exception:
                    return False

            try:
                rows = list(tp.query(primary_sql))
                contentions: List[Dict[str, Any]] = []
                columns = None
                for r in rows:
                    if columns is None:
                        columns = list(r.__dict__.keys())
                    item = format_query_result_row(r, columns)
                    # Add severity and heuristic main thread flag
                    blocked_name = item.get("blocked_thread_name")
                    blocked_is_main = _heuristic_is_main(blocked_name)
                    max_blocked_ms = float(item.get("max_blocked_ms") or 0.0)
                    avg_blocked_ms = float(item.get("avg_blocked_ms") or 0.0)
                    total_blocked_ms = float(item.get("total_blocked_ms") or 0.0)
                    item["blocked_is_main_thread"] = blocked_is_main
                    item["severity"] = self._classify_severity(blocked_is_main, max_blocked_ms, avg_blocked_ms, total_blocked_ms)
                    contentions.append(item)

                result: Dict[str, Any] = {
                    "totalCount": len(contentions),
                    "contentions": contentions,
                    "filters": {"process_name": process_name},
                    "analysisSource": "monitor_contention",
                    "primaryDataUnavailable": False,
                    "timeRangeMs": (time_range if (time_range and isinstance(time_range, dict)) else None),
                    "thresholds": {"min_block_ms": float(min_block_ms)},
                    "dataDependencies": ["android.monitor_contention"],
                    "notes": notes,
                }

                # Examples (from android_monitor_contention) if requested
                if include_examples:
                    examples_where = [f"p.name = '{safe_proc}'"]
                    if start_ns is not None and end_ns is not None:
                        examples_where.append(f"(amc.ts + amc.dur >= {start_ns} AND amc.ts <= {end_ns})")
                    if min_block_ns > 0:
                        examples_where.append(f"amc.dur >= {min_block_ns}")
                    examples_where_sql = " AND ".join(examples_where)
                    examples_sql = f"""
                    INCLUDE PERFETTO MODULE android.monitor_contention;
                    SELECT 
                      amc.ts/1e6 AS ts_ms,
                      amc.dur/1e6 AS dur_ms,
                      amc.blocked_thread_name,
                      amc.blocking_thread_name,
                      amc.short_blocking_method_name,
                      amc.waiter_count
                    FROM android_monitor_contention amc
                    JOIN process p USING(upid)
                    WHERE {examples_where_sql}
                    ORDER BY amc.dur DESC
                    LIMIT {example_limit};
                    """
                    try:
                        ex_rows = list(tp.query(examples_sql))
                        ex_cols = None
                        examples = []
                        for er in ex_rows:
                            if ex_cols is None:
                                ex_cols = list(er.__dict__.keys())
                            examples.append(format_query_result_row(er, ex_cols))
                        result["examples"] = examples
                        result["dataDependencies"].append("process")
                    except Exception:
                        notes.append("Failed to fetch examples from monitor_contention")

                # Per-thread breakdown (from thread_state) if requested
                if include_per_thread_breakdown:
                    breakdown, breakdown_notes = self._compute_blocked_state_breakdown(
                        tp, process_name, start_ns, end_ns, group_limit
                    )
                    result["blocked_state_breakdown"] = breakdown
                    notes.extend(breakdown_notes)
                    result["dataDependencies"].append("thread_state")

                    # Also compute top D-state functions if available
                    top_funcs, used_sbr = self._compute_top_dstate_functions(tp, process_name, start_ns, end_ns, min_block_ns, group_limit)
                    if top_funcs is not None:
                        result["top_dstate_functions"] = top_funcs
                        result["usedSchedBlockedReason"] = used_sbr
                        if used_sbr:
                            result["dataDependencies"].append("sched_blocked_reason")

                return result
            except Exception as e:
                msg = str(e)
                if self._is_monitor_contention_unavailable(msg):
                    # Run scheduler fallback
                    fallback_result = self._scheduler_fallback(
                        tp,
                        process_name,
                        start_ns,
                        end_ns,
                        min_block_ns,
                        include_per_thread_breakdown,
                        include_examples,
                        group_limit,
                        example_limit,
                    )
                    fallback_result.update({
                    "timeRangeMs": (time_range if (time_range and isinstance(time_range, dict)) else None),
                    "thresholds": {"min_block_ms": float(min_block_ms)},
                    "dataDependencies": ["thread_state"],
                    "notes": notes,
                    "filters": {"process_name": process_name},
                        "primaryDataUnavailable": True,
                        "fallbackNotice": "Monitor contention data unavailable; using scheduler-inferred fallback",
                    })
                    return fallback_result
                raise

        return self.run_formatted(trace_path, process_name, _op)

    # -------------------------
    # Fallback implementation
    # -------------------------
    def _is_monitor_contention_unavailable(self, error_msg: str) -> bool:
        """Check if the error indicates monitor contention data is unavailable."""
        msg_lower = error_msg.lower()
        return (
            "android_monitor_contention" in error_msg
            or "android.monitor_contention" in error_msg
            or "no such" in msg_lower
        )

    def _scheduler_fallback(
        self,
        tp,
        process_name: str,
        start_ns: int | None,
        end_ns: int | None,
        min_block_ns: int,
        include_per_thread_breakdown: bool,
        include_examples: bool,
        group_limit: int,
        example_limit: int,
    ) -> Dict[str, Any]:
        """Run scheduler-based fallback analysis for thread contention."""
        safe_proc = process_name.replace("'", "''")

        time_filter = []
        if start_ns is not None and end_ns is not None:
            time_filter.append(f"AND ts.ts + ts.dur >= {start_ns} AND ts.ts <= {end_ns}")
        dur_filter = f"AND ts.dur >= {min_block_ns}" if min_block_ns > 0 else ""
        time_filter_sql = " ".join(time_filter)

        # Pair-level aggregation with waker linkage
        pairs_sql = f"""
        WITH target AS (
          SELECT upid FROM process WHERE name = '{safe_proc}'
        ), ts AS (
          SELECT ts.ts AS ts, ts.dur AS dur, ts.utid AS utid, ts.state AS state, ts.waker_utid AS waker_utid
          FROM thread_state ts
          JOIN thread t USING(utid)
          JOIN process p USING(upid)
          WHERE p.upid = (SELECT upid FROM target)
            AND ts.state IN ('S','D')
            {dur_filter}
            {time_filter_sql}
        )
        SELECT
          bt.name AS blocked_thread_name,
          bt.is_main_thread AS blocked_is_main_thread,
          wt.name AS waker_thread_name,
          SUM(ts.dur)/1e6 AS total_blocked_ms,
          AVG(ts.dur)/1e6 AS avg_blocked_ms,
          MAX(ts.dur)/1e6 AS max_blocked_ms,
          COUNT(*) AS blocked_events
        FROM ts
        JOIN thread bt ON bt.utid = ts.utid
        LEFT JOIN thread wt ON wt.utid = ts.waker_utid
        GROUP BY blocked_thread_name, blocked_is_main_thread, waker_thread_name
        ORDER BY total_blocked_ms DESC
        LIMIT {group_limit};
        """

        try:
            pairs_rows = list(tp.query(pairs_sql))
        except Exception:
            # If even scheduler data is unavailable, return empty result
            return {
                "totalCount": 0,
                "contentions": [],
                "analysisSource": "scheduler_inferred",
                "usesWakerLinkage": False,
                "usedSchedBlockedReason": False,
            }

        # Check if we have any waker linkage
        has_waker_linkage = any(getattr(r, 'waker_thread_name', None) for r in pairs_rows)

        contentions: List[Dict[str, Any]] = []
        for r in pairs_rows:
            blocked_is_main = bool(getattr(r, 'blocked_is_main_thread', 0) or 0)
            max_blocked_ms = float(getattr(r, 'max_blocked_ms', 0.0) or 0.0)
            avg_blocked_ms = float(getattr(r, 'avg_blocked_ms', 0.0) or 0.0)
            total_blocked_ms = float(getattr(r, 'total_blocked_ms', 0.0) or 0.0)

            severity = self._classify_severity(blocked_is_main, max_blocked_ms, avg_blocked_ms, total_blocked_ms)

            contentions.append({
                'blocked_thread_name': getattr(r, 'blocked_thread_name', None),
                'blocking_thread_name': getattr(r, 'waker_thread_name', None),
                'short_blocking_method_name': None,
                'contention_count': int(getattr(r, 'blocked_events', 0) or 0),
                'total_blocked_ms': total_blocked_ms,
                'avg_blocked_ms': avg_blocked_ms,
                'max_blocked_ms': max_blocked_ms,
                'total_waiters': None,
                'max_concurrent_waiters': None,
                'blocked_is_main_thread': blocked_is_main,
                'severity': severity,
            })

        result: Dict[str, Any] = {
            "totalCount": len(contentions),
            "contentions": contentions,
            "analysisSource": "scheduler_inferred",
            "usesWakerLinkage": has_waker_linkage,
        }

        # Compute top D-state functions (time-scoped), if available
        used_sched_blocked_reason = False
        try:
            time_filter2 = []
            if start_ns is not None and end_ns is not None:
                time_filter2.append(f"AND ts.ts + ts.dur >= {start_ns} AND ts.ts <= {end_ns}")
            dur_filter2 = f"AND ts.dur >= {min_block_ns}" if min_block_ns > 0 else ""
            time_filter2_sql = " ".join(time_filter2)

            causes_sql = f"""
            WITH target AS (
              SELECT upid FROM process WHERE name = '{safe_proc}'
            ), ts AS (
              SELECT ts, dur, utid, state FROM thread_state ts
              JOIN thread USING(utid)
              JOIN process USING(upid)
              WHERE upid = (SELECT upid FROM target) AND state = 'D'
                {dur_filter2}
                {time_filter2_sql}
            )
            SELECT sbr.blocked_function, SUM(ts.dur)/1e6 AS total_blocked_ms
            FROM ts
            JOIN sched_blocked_reason sbr
              ON sbr.utid = ts.utid AND sbr.ts BETWEEN ts.ts AND ts.ts + ts.dur
            GROUP BY sbr.blocked_function
            ORDER BY total_blocked_ms DESC
            LIMIT {group_limit};
            """
            cause_rows = list(tp.query(causes_sql))
            if cause_rows:
                used_sched_blocked_reason = True
                top_funcs: List[Dict[str, Any]] = []
                ccols = None
                for cr in cause_rows:
                    if ccols is None:
                        ccols = list(cr.__dict__.keys())
                    top_funcs.append(format_query_result_row(cr, ccols))
                result["top_dstate_functions"] = top_funcs
        except Exception:
            # sched_blocked_reason not available - continue without it
            used_sched_blocked_reason = False

        result["usedSchedBlockedReason"] = used_sched_blocked_reason

        # Per-thread breakdown if requested
        if include_per_thread_breakdown:
            breakdown, breakdown_notes = self._compute_blocked_state_breakdown(
                tp, process_name, start_ns, end_ns, group_limit
            )
            result["blocked_state_breakdown"] = breakdown
            # Attach notes at caller level

        # Examples from thread_state if requested (longest waits)
        if include_examples:
            tf = []
            if start_ns is not None and end_ns is not None:
                tf.append(f"AND ts.ts + ts.dur >= {start_ns} AND ts.ts <= {end_ns}")
            durf = f"AND ts.dur >= {min_block_ns}" if min_block_ns > 0 else ""
            tf_sql = " ".join(tf)
            examples_sql = f"""
            WITH target AS (
              SELECT upid FROM process WHERE name = '{safe_proc}'
            )
            SELECT 
              ts.ts/1e6 AS ts_ms,
              ts.dur/1e6 AS dur_ms,
              bt.name AS blocked_thread_name,
              wt.name AS waker_thread_name,
              NULL AS short_blocking_method_name
            FROM thread_state ts
            JOIN thread bt ON bt.utid = ts.utid
            JOIN process p ON p.upid = bt.upid
            LEFT JOIN thread wt ON wt.utid = ts.waker_utid
            WHERE p.name = '{safe_proc}'
              AND ts.state IN ('S','D')
              {durf}
              {tf_sql}
            ORDER BY ts.dur DESC
            LIMIT {example_limit};
            """
            try:
                ex_rows = list(tp.query(examples_sql))
                ex_cols = None
                examples = []
                for er in ex_rows:
                    if ex_cols is None:
                        ex_cols = list(er.__dict__.keys())
                    examples.append(format_query_result_row(er, ex_cols))
                result["examples"] = examples
            except Exception:
                # Ignore examples errors in fallback
                pass

        return result

    def _compute_blocked_state_breakdown(
        self,
        tp,
        process_name: str,
        start_ns: int | None,
        end_ns: int | None,
        limit: int,
    ) -> tuple[list[dict], list[str]]:
        """Compute per-thread S/D totals and percentages for the window."""
        safe_proc = process_name.replace("'", "''")
        notes: List[str] = []

        tf = []
        if start_ns is not None and end_ns is not None:
            tf.append(f"AND ts + dur >= {start_ns} AND ts <= {end_ns}")
        tf_sql = " ".join(tf)

        breakdown_sql = f"""
        WITH t AS (
          SELECT ts, dur, utid, state
          FROM thread_state
          JOIN thread USING(utid)
          JOIN process USING(upid)
          WHERE process.name = '{safe_proc}'
            AND state IN ('S','D')
            {tf_sql}
        )
        SELECT 
          thread.name AS thread_name,
          thread.is_main_thread AS is_main_thread,
          t.state AS state,
          SUM(t.dur)/1e6 AS total_ms
        FROM t
        JOIN thread USING(utid)
        GROUP BY thread_name, is_main_thread, state
        ORDER BY total_ms DESC
        LIMIT {limit};
        """

        breakdown_rows = []
        try:
            breakdown_rows = list(tp.query(breakdown_sql))
        except Exception:
            notes.append("Failed to compute blocked_state_breakdown")
            return [], notes

        # Estimate window duration for percentage
        if start_ns is not None and end_ns is not None:
            window_ns = max(end_ns - start_ns, 1)
        else:
            # Derive from process thread_state coverage
            try:
                win_sql = f"""
                SELECT (MAX(ts + dur) - MIN(ts)) AS win
                FROM thread_state
                JOIN thread USING(utid)
                JOIN process USING(upid)
                WHERE process.name = '{safe_proc}'
                """
                win_rows = list(tp.query(win_sql))
                window_ns = int(getattr(win_rows[0], 'win', 0) or 0) if win_rows else 0
                if not window_ns:
                    window_ns = 1
            except Exception:
                window_ns = 1
                notes.append("Failed to compute window duration for percentages; using 1ns fallback")

        bcols = None
        breakdown: List[Dict[str, Any]] = []
        for br in breakdown_rows:
            if bcols is None:
                bcols = list(br.__dict__.keys())
            row = format_query_result_row(br, bcols)
            total_ms = float(row.get('total_ms') or 0.0)
            percent = (total_ms * 1_000_000.0) / float(window_ns) * 100.0
            row['percent_of_trace_window'] = percent
            breakdown.append(row)

        return breakdown, notes

    def _classify_severity(self, is_main_thread: bool, max_blocked_ms: float, avg_blocked_ms: float, total_blocked_ms: float) -> str:
        """Classify contention severity based on thresholds."""
        if is_main_thread and max_blocked_ms > 100:
            return "CRITICAL"
        elif max_blocked_ms > 500 or total_blocked_ms > 1000:
            return "HIGH"
        elif avg_blocked_ms > 50:
            return "MEDIUM"
        else:
            return "LOW"

