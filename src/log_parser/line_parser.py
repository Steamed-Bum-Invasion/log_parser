import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class session:
    session_id: int
    date: str
    start_time: str
    end_time: Optional[str] = None
    pallets_produced: int = 0
    init_total_time: Optional[float] = None
    final_total_time: Optional[float] = None


TIMESTAMP_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2},\d{3})"
)

INIT_RE = re.compile(r"Application initialized")

METRICS_RE = re.compile(
    r"TotalUnits:\s*(?P<total_units>\d+).*?"
    r"TotalTime:\s*(?P<total_time>\d+(?:\.\d+)?)"
)


def read_log(file_path: str) -> List[session]:
    sessions: List[session] = []
    current_session: Optional[session] = None
    session_count = 0

    last_timestamp = None

    # Track metrics for current session
    init_units = None
    last_units = None
    init_time = None
    last_time = None
    metrics_count = 0  # Track how many metrics lines we've seen in current session

    with open(file_path, "r") as f:
        for line in f:
            ts = TIMESTAMP_RE.match(line)
            if ts:
                last_timestamp = ts

            if INIT_RE.search(line):
                if not last_timestamp:
                    continue

                # close previous session
                if current_session:
                    current_session.end_time = last_timestamp["time"]

                    # Calculate based on number of metrics lines
                    if metrics_count == 0:
                        # No metrics in this session
                        current_session.pallets_produced = 0
                        current_session.init_total_time = None
                        current_session.final_total_time = None
                    elif metrics_count == 1:
                        # Only one metrics line - pallets = 1, time delta = None
                        current_session.pallets_produced = 1
                        current_session.init_total_time = init_time
                        current_session.final_total_time = last_time
                    else:
                        # Multiple metrics lines - calculate delta
                        current_session.pallets_produced = (
                            last_units - init_units
                            if init_units is not None and last_units is not None
                            else 0
                        )
                        current_session.init_total_time = init_time
                        current_session.final_total_time = last_time

                    sessions.append(current_session)

                # start new session
                session_count += 1
                current_session = session(
                    session_id=session_count,
                    date=last_timestamp["date"],
                    start_time=last_timestamp["time"],
                )

                # Reset metrics for new session
                init_units = None
                last_units = None
                init_time = None
                last_time = None
                metrics_count = 0

            # Process metrics - they come AFTER init
            metrics = METRICS_RE.search(line)
            if metrics and current_session:
                units = int(metrics["total_units"])
                total_time = float(metrics["total_time"])
                metrics_count += 1

                # First metrics in session become the baseline
                if init_units is None:
                    init_units = units
                    init_time = total_time

                # Always update last known values
                last_units = units
                last_time = total_time

    # close final session
    if current_session and last_timestamp:
        current_session.end_time = last_timestamp["time"]

        # Calculate based on number of metrics lines
        if metrics_count == 0:
            # No metrics in this session
            current_session.pallets_produced = 0
            current_session.init_total_time = None
            current_session.final_total_time = None
        elif metrics_count == 1:
            # Only one metrics line - pallets = 1, time delta = None
            current_session.pallets_produced = 1
            current_session.init_total_time = init_time
            current_session.final_total_time = last_time
        else:
            # Multiple metrics lines - calculate delta
            current_session.pallets_produced = (
                last_units - init_units
                if init_units is not None and last_units is not None
                else 0
            )
            current_session.init_total_time = init_time
            current_session.final_total_time = last_time

        sessions.append(current_session)

    return sessions


def write_sessions_to_file(sessions: List[session], output_file: str):
    with open(output_file, "w") as f:
        for s in sessions:
            f.write(
                f"Session {s.session_id}\n"
                f"Date: {s.date}\n"
                f"Start Time: {s.start_time}\n"
                f"End Time: {s.end_time}\n"
                f"Pallets Produced: {s.pallets_produced}\n"
                f"Init Total Time: {s.init_total_time}\n"
                f"Final Total Time: {s.final_total_time}\n"
                f"{'-' * 40}\n"
            )
