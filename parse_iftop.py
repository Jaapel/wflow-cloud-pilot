from itertools import chain
from pathlib import Path
from re import match
from typing import Any, Dict, List

import pandas as pd
from dateutil.parser import parse


def parse_single_iftop_log(filepath: Path):
    """
    parse single file
    """
    with filepath.open("r") as f:
        lines: List[str] = f.readlines()[3:]

        htop_cols = (
            "#",
            "host/name",
            "direction",
            "2s",
            "10s",
            "40s",
            "cumulative",
            "t",
        )

        res = []

        def key_line(line: str) -> Dict[str, Any]:
            if "=>" in line:
                cols = htop_cols
            else:
                cols = htop_cols[1:]

            values = line.split() + [filepath.stem]
            return dict(zip(cols, values))

        for line in lines:
            if line.startswith("---"):
                break
            else:
                res.append(key_line(line))

        return res


def human_readable_to_bytes(size: str):
    """
    Convert human readable file size to bytes.
    """
    units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}
    # Alternative unit definitions, notably used by Windows:# units = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40}def parse_size(size):
    number, unit = match(r"([0-9.]+)(\w*)", size).groups()
    return int(float(number) * units[unit])


def parse_directory(dir: str) -> pd.DataFrame:
    """
    parse directory
    """
    path = Path(dir)

    parsed_logs = list(filter(bool, map(parse_single_iftop_log, path.glob("*.log"))))
    parsed_logs = list(chain(*parsed_logs))

    df = pd.DataFrame(parsed_logs)
    df["cumulative_parsed"] = df["cumulative"].apply(human_readable_to_bytes)
    df["t_parsed"] = pd.to_datetime(df["t"], format="%H-%M-%S.%f")
    return df


if __name__ == "__main__":
    logs_dir = "logs"
    df = parse_directory(logs_dir)
    df.to_csv("network_usage.csv")
