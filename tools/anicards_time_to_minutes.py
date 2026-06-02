#!/usr/bin/env python3
"""Convert the AniCards "Time" stat from days to minutes.

AniCards renders anime watch time in days (e.g. "88.7d"). This rewrites that
value in place to minutes (days * 1440), formatted with thousands separators
and an 'm' suffix (e.g. "127,728m"). Manga has no Time stat, so only the Anime
column is touched.

Run it after re-downloading card.svg from anicards.alpha49.com:

    python tools/anicards_time_to_minutes.py card.svg

It's idempotent (a value already in minutes ends in 'm', not 'd', so a second
run is a no-op) and exits non-zero if it finds nothing to convert.

Note: AniCards rounds days to one decimal, so the minutes value is accurate to
within ~1 day's rounding (about +/- 12 hours).
"""
import re
import sys

DAY_MINUTES = 24 * 60  # 1440

# The stat-value that follows a "Time" label and ends in 'd' (the day count).
TIME_DAYS = re.compile(r'(>Time</text>\s*<text\b[^>]*>)([\d,.]+)d(</text>)')


def _to_minutes(match: "re.Match[str]") -> str:
    prefix, days, suffix = match.group(1), match.group(2), match.group(3)
    minutes = round(float(days.replace(",", "")) * DAY_MINUTES)
    return f"{prefix}{minutes:,}m{suffix}"


def convert(svg: str) -> "tuple[str, int]":
    return TIME_DAYS.subn(_to_minutes, svg)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python tools/anicards_time_to_minutes.py <card.svg>")
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    new_svg, n = convert(svg)
    if n == 0:
        sys.exit("No 'Time' value in days (e.g. '88.7d') found - nothing changed.")
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_svg)
    print(f"Converted {n} 'Time' value(s) from days to minutes in {path}")


if __name__ == "__main__":
    main()
