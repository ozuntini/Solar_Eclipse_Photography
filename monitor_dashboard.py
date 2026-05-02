#!/usr/bin/env python3
"""
Eclipse Photography — Monitoring Dashboard (Streamlit)

Reads the JSONL action journal and displays in real-time:
  - the last completed action
  - the next scheduled action

Usage:
    streamlit run monitor_dashboard.py -- --journal eclipse_journal.jsonl
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# How often the dashboard auto-refreshes for the clock (seconds)
REFRESH_CLOCK_SECONDS = 1

# How often the JSONL journal file is re-read (seconds)
REFRESH_JOURNAL_SECONDS = 10

# ---------------------------------------------------------------------------
# Argument parsing (Streamlit strips everything before "--")
# ---------------------------------------------------------------------------

def _get_journal_path() -> str:
    """Return the journal file path from CLI args or default."""
    args = sys.argv[1:]
    try:
        idx = args.index("--journal")
    except ValueError:
        return "eclipse_journal.jsonl"
    if idx + 1 >= len(args):
        print(
            "[monitor_dashboard] Warning: --journal requires a value; using default.",
            file=sys.stderr,
        )
        return "eclipse_journal.jsonl"
    return args[idx + 1]


# ---------------------------------------------------------------------------
# Journal reading helpers
# ---------------------------------------------------------------------------

ACTION_EVENTS = {"PHOTO_TRIGGER", "FILTER_MOVE", "ACTION_COMPLETE"}

EVENT_ICONS = {
    "PHOTO_TRIGGER": "📷",
    "FILTER_MOVE": "🔭",
    "ACTION_COMPLETE": "✅",
    "SESSION_START": "🚀",
    "SESSION_END": "🏁",
}


def _parse_journal(path: str) -> list[dict]:
    """Read *all* valid JSON lines from the journal and return them as a list."""
    entries: list[dict] = []
    p = Path(path)
    if not p.exists():
        return entries
    with p.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"[monitor_dashboard] Malformed JSON line ignored: {exc}", file=sys.stderr)
    return entries


def _last_action_entry(entries: list[dict]) -> dict | None:
    """Return the most recent entry whose event is in ACTION_EVENTS."""
    for entry in reversed(entries):
        if entry.get("event") in ACTION_EVENTS:
            return entry
    return None


# ---------------------------------------------------------------------------
# UI rendering helpers
# ---------------------------------------------------------------------------

def _status_widget(status: str) -> None:
    """Render status with appropriate Streamlit component."""
    if status == "SUCCESS":
        st.success(f"✅ {status}")
    elif status == "ERROR":
        st.error(f"❌ {status}")
    elif status == "SKIPPED":
        st.warning(f"⚠️ {status}")
    else:
        st.info(f"ℹ️ {status}")


def _render_last_action(entry: dict) -> None:
    """Render the 'Dernière action réalisée' block."""
    event = entry.get("event", "")
    icon = EVENT_ICONS.get(event, "⚙️")
    current = entry.get("current_action") or {}
    details = entry.get("details") or {}

    with st.container(border=True):
        st.subheader(f"{icon} Dernière action réalisée")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Timestamp :** {entry.get('timestamp', '—')}")
            st.write(f"**Séquence n° :** {entry.get('seq', '—')}")
            st.write(f"**Événement :** `{event}`")
        with col2:
            st.write(f"**Description :** {current.get('description', '—')}")
            _status_widget(str(entry.get("status", "—")))

        # Extra details per event type
        if event == "PHOTO_TRIGGER":
            ok = details.get("cameras_success", "?")
            total = details.get("cameras_total", "?")
            st.write(f"📸 Appareils déclenchés : **{ok} / {total}**")
        elif event == "FILTER_MOVE":
            direction_raw = details.get("direction", "")
            direction_label = {
                "OPEN": "Ouverture",
                "CLOSE": "Fermeture",
            }.get(str(direction_raw).upper(), direction_raw)
            st.write(f"🔭 Direction du filtre : **{direction_label}**")


def _render_next_action(entry: dict) -> None:
    """Render the 'Prochaine action' block."""
    next_action = entry.get("next_action")

    with st.container(border=True):
        st.subheader("⏭️ Prochaine action")
        if next_action:
            st.write(f"**Type :** `{next_action.get('type', '—')}`")
            st.write(f"**Description :** {next_action.get('description', '—')}")
            scheduled = next_action.get("scheduled_at")
            st.write(f"**Heure prévue :** {scheduled if scheduled else '—'}")
        else:
            st.info("✅ Séquence terminée — aucune action suivante")


def _render_history(entries: list[dict]) -> None:
    """Render the last-10-entries expander."""
    with st.expander("📋 Historique récent", expanded=False):
        if not entries:
            st.write("Aucune entrée disponible.")
            return

        recent = entries[-10:]
        rows = []
        for e in reversed(recent):
            current = e.get("current_action") or {}
            rows.append(
                {
                    "timestamp": e.get("timestamp", ""),
                    "seq": e.get("seq", ""),
                    "event": e.get("event", ""),
                    "description": current.get("description", ""),
                    "status": e.get("status", ""),
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True)


def _format_last_read_ts(ts: float | None) -> str:
    """Return a human-readable last-read timestamp, or 'Jamais' if not yet read."""
    if ts is None:
        return "Jamais"
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_last_read_ts(ts: float) -> str:
    """Return a human-readable HH:MM:SS string for a Unix timestamp, or '—' if unset."""
    if ts > 0:
        return datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    return "—"


# ---------------------------------------------------------------------------
# Main dashboard
# ---------------------------------------------------------------------------
    journal_path = _get_journal_path()

    st.set_page_config(
        page_title="Eclipse Photography — Monitoring",
        page_icon="🌑",
        layout="wide",
    )

    # --- Session state init ---
    if "last_log_read_ts" not in st.session_state:
        st.session_state.last_log_read_ts = None  # triggers immediate read on first run
        st.session_state.entries = []
        st.session_state.last_entry = None
        st.session_state.total_lines = 0

    # --- Header with digital clock ---
    header_col, clock_col = st.columns([4, 1])
    with header_col:
        st.title("🌑 Eclipse Photography — Monitoring en temps réel")
        st.caption(f"Fichier journal surveillé : `{journal_path}`")
    with clock_col:
        st.markdown(
            f"<div style='text-align:right; font-size:2rem; font-weight:bold; "
            f"font-family:monospace; padding-top:0.5rem;'>"
            f"🕒 {datetime.now().strftime('%H:%M:%S')}</div>",
            unsafe_allow_html=True,
        )

    # --- Conditionally re-read journal (every 10 s) ---
    now_ts = time.time()
    if (
        st.session_state.last_log_read_ts is None
        or now_ts - st.session_state.last_log_read_ts >= REFRESH_JOURNAL_SECONDS
    ):
        st.session_state.last_log_read_ts = now_ts
        entries = _parse_journal(journal_path)
        st.session_state.entries = entries
        st.session_state.total_lines = len(entries)
        st.session_state.last_entry = _last_action_entry(entries)

    entries = st.session_state.entries
    last_entry = st.session_state.last_entry
    total_lines = st.session_state.total_lines

    # Test-mode banner (shown if any entry has test_mode == True)
    if any((e.get("details") or {}).get("test_mode") for e in entries):
        st.warning("🧪 **Mode test activé** — aucune photo réelle ne sera prise")

    # --- No data state ---
    if not entries or last_entry is None:
        file_exists = Path(journal_path).exists()
        if not file_exists:
            st.info(
                "⏳ En attente du démarrage de la séquence... (fichier non trouvé)"
            )
        else:
            st.info("⏳ En attente du démarrage de la séquence...")
        st.divider()
        last_read_str = _format_last_read_ts(st.session_state.last_log_read_ts)
        st.caption(
            f"Entrées lues : {total_lines}  •  "
            f"Dernière lecture du journal : "
            f"{_format_last_read_ts(st.session_state.last_log_read_ts)}"
        )
        time.sleep(REFRESH_CLOCK_SECONDS)
        st.rerun()

    # --- Last action block ---
    _render_last_action(last_entry)

    st.divider()

    # --- Next action block ---
    _render_next_action(last_entry)

    st.divider()

    # --- History ---
    _render_history(entries)

    # --- Status bar ---
    last_read_str = _format_last_read_ts(st.session_state.last_log_read_ts)
    st.caption(
        f"Entrées lues : {total_lines}  •  "
        f"Dernière lecture du journal : "
        f"{_format_last_read_ts(st.session_state.last_log_read_ts)}"
    )

    # --- Auto-refresh every 1 s (for the clock) ---
    time.sleep(REFRESH_CLOCK_SECONDS)
    st.rerun()


if __name__ == "__main__":
    main()
