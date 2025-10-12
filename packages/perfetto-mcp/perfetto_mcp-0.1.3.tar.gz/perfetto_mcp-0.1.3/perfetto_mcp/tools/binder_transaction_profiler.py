"""Binder transaction profiler using android.binder module."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from .base import BaseTool, ToolError
from ..utils.query_helpers import format_query_result_row

logger = logging.getLogger(__name__)


class BinderTransactionProfilerTool(BaseTool):
    """Analyze binder transaction performance and identify bottlenecks.

    Uses the android.binder module to compute client/server latencies, overhead,
    and optionally includes a breakdown of thread states during the transaction.
    """

    def binder_transaction_profiler(
        self,
        trace_path: str,
        process_filter: str,
        min_latency_ms: float = 10.0,
        include_thread_states: bool = True,
        time_range: dict | None = None,
        correlate_with_main_thread: bool = False,
        group_by: str | None = None,
    ) -> str:
        """Profile binder transactions for a process as client or server.

        Parameters
        ----------
        trace_path : str
            Path to the Perfetto trace file.
        process_filter : str
            Process name to match either as client or server process in binder txns.
        min_latency_ms : float, optional
            Minimum client latency to include (ms). Default: 10.0.
        include_thread_states : bool, optional
            If true, includes top thread states per transaction (aggregated). Default: True.
        time_range : dict | None, optional
            Optional window filter: {'start_ms': X, 'end_ms': Y}. Filters by client_ts in range.
        correlate_with_main_thread : bool, optional
            If true, adds best-effort main-thread state summary for client main-thread txns.
        group_by : str | None, optional
            Aggregate view. One of: None (detailed rows), 'aidl', 'server_process'.

        Returns
        -------
        str
            JSON envelope with fields: processName, tracePath, success, error, result.
            Result shape (detailed rows when group_by is None):
              {
                totalCount: number,
                timeRangeMs?: { start_ms?, end_ms? },
                transactions: [
                  {
                    client_process, server_process, aidl_name, method_name,
                    client_latency_ms, server_latency_ms, overhead_ms, overhead_ratio,
                    is_main_thread, is_sync, top_thread_states, main_thread_top_states?,
                    latency_severity
                  }
                ],
                filters: { process_filter, min_latency_ms, include_thread_states, correlate_with_main_thread, group_by }
              }

            When group_by is provided, returns aggregates instead of transactions:
              {
                totalCount: number,
                timeRangeMs?: { start_ms?, end_ms? },
                aggregates: [ ... ],
                filters: { ..., group_by }
              }
        """

        def _op(tp):
            if not process_filter or not isinstance(process_filter, str):
                raise ToolError("INVALID_PARAMETERS", "process_filter must be a non-empty string")
            try:
                _ = float(min_latency_ms)
            except Exception:
                raise ToolError("INVALID_PARAMETERS", "min_latency_ms must be numeric")

            # Validate group_by
            valid_groups = {None, "aidl", "server_process"}
            if group_by not in valid_groups:
                raise ToolError("INVALID_PARAMETERS", "group_by must be one of: None, 'aidl', 'server_process'")

            # Validate time_range
            start_ns = None
            end_ns = None
            time_range_ms: dict | None = None
            if time_range is not None:
                if not isinstance(time_range, dict):
                    raise ToolError("INVALID_PARAMETERS", "time_range must be a dict with start_ms/end_ms")
                start_ms = time_range.get("start_ms")
                end_ms = time_range.get("end_ms")
                def _num(x):
                    try:
                        return float(x)
                    except Exception:
                        return None
                if start_ms is not None:
                    start_val = _num(start_ms)
                    if start_val is None:
                        raise ToolError("INVALID_PARAMETERS", "time_range.start_ms must be numeric")
                    start_ns = int(start_val * 1e6)
                if end_ms is not None:
                    end_val = _num(end_ms)
                    if end_val is None:
                        raise ToolError("INVALID_PARAMETERS", "time_range.end_ms must be numeric")
                    end_ns = int(end_val * 1e6)
                if start_ns is not None and end_ns is not None and start_ns > end_ns:
                    raise ToolError("INVALID_PARAMETERS", "time_range.start_ms must be <= end_ms")
                time_range_ms = {k: v for k, v in {"start_ms": start_ms, "end_ms": end_ms}.items() if v is not None}

            safe_proc = process_filter.replace("'", "''")

            # Build the conditional projection for thread states
            if include_thread_states:
                top_states_sql = (
                    "(SELECT GROUP_CONCAT(thread_state || ':' || CAST(state_duration_ms AS TEXT) || 'ms', ', ') "
                    "FROM thread_state_breakdown tsb "
                    "WHERE tsb.binder_txn_id = ba.binder_txn_id "
                    "ORDER BY state_duration_ms DESC LIMIT 3) AS top_thread_states"
                )
            else:
                top_states_sql = "NULL AS top_thread_states"

            # Optional best-effort main thread state correlation for client main-thread transactions
            if correlate_with_main_thread:
                client_main_states_sql = (
                    "CASE WHEN ba.is_main_thread THEN "
                    "(SELECT GROUP_CONCAT(thread_state || ':' || CAST(state_duration_ms AS TEXT) || 'ms', ', ') "
                    " FROM thread_state_breakdown tsb "
                    " WHERE tsb.binder_txn_id = ba.binder_txn_id "
                    "   AND LOWER(tsb.thread_state_type) LIKE 'client%' "
                    " ORDER BY state_duration_ms DESC LIMIT 3) "
                    "ELSE NULL END AS main_thread_top_states"
                )
            else:
                client_main_states_sql = "NULL AS main_thread_top_states"

            # Time window conditions
            time_predicates = []
            if start_ns is not None:
                time_predicates.append(f"client_ts >= {start_ns}")
            if end_ns is not None:
                time_predicates.append(f"client_ts <= {end_ns}")
            time_window_where = (" AND " + " AND ".join(time_predicates)) if time_predicates else ""

            sql_query = f"""
            INCLUDE PERFETTO MODULE android.binder;

            WITH binder_analysis AS (
              SELECT 
                binder_txn_id,
                client_process,
                server_process,
                aidl_name,
                method_name,
                client_ts,
                client_dur,
                server_ts,
                server_dur,
                is_main_thread,
                is_sync,
                client_tid,
                server_tid
              FROM android_binder_txns
              WHERE (client_process = '{safe_proc}' OR server_process = '{safe_proc}')
                AND client_dur >= {float(min_latency_ms)} * 1e6
                {time_window_where}
            ),
            thread_state_breakdown AS (
              SELECT 
                binder_txn_id,
                thread_state_type,
                thread_state,
                SUM(thread_state_dur) / 1e6 as state_duration_ms
              FROM android_sync_binder_thread_state_by_txn
              WHERE binder_txn_id IN (SELECT binder_txn_id FROM binder_analysis)
              GROUP BY binder_txn_id, thread_state_type, thread_state
            )
            SELECT 
              ba.client_process,
              ba.server_process,
              ba.aidl_name,
              ba.method_name,
              CAST(ba.client_dur / 1e6 AS REAL) as client_latency_ms,
              CAST(ba.server_dur / 1e6 AS REAL) as server_latency_ms,
              CAST((ba.client_dur - ba.server_dur) / 1e6 AS REAL) as overhead_ms,
              CAST((ba.client_dur - ba.server_dur) AS REAL) / NULLIF(ba.client_dur, 0) AS overhead_ratio,
              ba.is_main_thread,
              ba.is_sync,
              {top_states_sql},
              {client_main_states_sql},
              CASE
                WHEN ba.client_dur > 100e6 AND ba.is_main_thread THEN 'CRITICAL'
                WHEN ba.client_dur > 50e6 THEN 'HIGH'
                WHEN ba.client_dur > 20e6 THEN 'MEDIUM'
                ELSE 'LOW'
              END as latency_severity
            FROM binder_analysis ba
            ORDER BY ba.client_dur DESC;
            """

            try:
                # If an aggregate view is requested, run a different projection
                if group_by is None:
                    rows = list(tp.query(sql_query))
                else:
                    if group_by == "aidl":
                        group_sql = f"""
                        INCLUDE PERFETTO MODULE android.binder;
                        WITH binder_analysis AS (
                          SELECT 
                            binder_txn_id,
                            client_process,
                            server_process,
                            aidl_name,
                            method_name,
                            client_ts,
                            client_dur,
                            server_dur,
                            is_main_thread
                          FROM android_binder_txns
                          WHERE (client_process = '{safe_proc}' OR server_process = '{safe_proc}')
                            AND client_dur >= {float(min_latency_ms)} * 1e6
                            {time_window_where}
                        )
                        SELECT 
                          aidl_name,
                          method_name,
                          COUNT(*) as txn_count,
                          CAST(AVG(client_dur) / 1e6 AS REAL) as avg_client_latency_ms,
                          CAST(AVG(server_dur) / 1e6 AS REAL) as avg_server_latency_ms,
                          CAST(AVG(client_dur - server_dur) / 1e6 AS REAL) as avg_overhead_ms,
                          AVG(CAST(client_dur - server_dur AS REAL) / NULLIF(client_dur, 0)) as avg_overhead_ratio,
                          SUM(CASE WHEN is_main_thread THEN 1 ELSE 0 END) as main_thread_txn_count
                        FROM binder_analysis
                        GROUP BY aidl_name, method_name
                        ORDER BY avg_client_latency_ms DESC;
                        """
                    elif group_by == "server_process":
                        group_sql = f"""
                        INCLUDE PERFETTO MODULE android.binder;
                        WITH binder_analysis AS (
                          SELECT 
                            binder_txn_id,
                            client_process,
                            server_process,
                            client_ts,
                            client_dur,
                            server_dur,
                            is_main_thread
                          FROM android_binder_txns
                          WHERE (client_process = '{safe_proc}' OR server_process = '{safe_proc}')
                            AND client_dur >= {float(min_latency_ms)} * 1e6
                            {time_window_where}
                        )
                        SELECT 
                          server_process,
                          COUNT(*) as txn_count,
                          CAST(AVG(client_dur) / 1e6 AS REAL) as avg_client_latency_ms,
                          CAST(AVG(server_dur) / 1e6 AS REAL) as avg_server_latency_ms,
                          CAST(AVG(client_dur - server_dur) / 1e6 AS REAL) as avg_overhead_ms,
                          AVG(CAST(client_dur - server_dur AS REAL) / NULLIF(client_dur, 0)) as avg_overhead_ratio,
                          SUM(CASE WHEN is_main_thread THEN 1 ELSE 0 END) as main_thread_txn_count
                        FROM binder_analysis
                        GROUP BY server_process
                        ORDER BY avg_client_latency_ms DESC;
                        """
                    else:
                        group_sql = sql_query  # fallback shouldn't happen

                    rows = list(tp.query(group_sql))
            except Exception as e:
                msg = str(e)
                # Common failures when binder module/views are unavailable
                if (
                    "android_binder_txns" in msg
                    or "android.binder" in msg
                    or "android_sync_binder_thread_state_by_txn" in msg
                    or "no such" in msg.lower()
                ):
                    raise ToolError(
                        "BINDER_DATA_UNAVAILABLE",
                        "Binder analysis data not available in this trace (module/views missing).",
                        details=msg,
                    )
                raise

            columns = None
            formatted_rows: List[Dict[str, Any]] = []
            for r in rows:
                if columns is None:
                    columns = list(r.__dict__.keys())
                formatted_rows.append(format_query_result_row(r, columns))

            result: Dict[str, Any] = {
                "totalCount": len(formatted_rows),
                "filters": {
                    "process_filter": process_filter,
                    "min_latency_ms": min_latency_ms,
                    "include_thread_states": include_thread_states,
                    "correlate_with_main_thread": correlate_with_main_thread,
                    "group_by": group_by,
                },
            }
            if time_range_ms:
                result["timeRangeMs"] = time_range_ms

            if group_by is None:
                result["transactions"] = formatted_rows
            else:
                result["aggregates"] = formatted_rows

            return result

        return self.run_formatted(trace_path, process_filter, _op)

