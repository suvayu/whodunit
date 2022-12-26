import csv
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
import re
from textwrap import dedent

import sh

from whodunit.metautils import Author, shtrip

BLANK_LINE = re.compile(r"\n\s*\n")
PART_HEADER = re.compile(r"(.+) \(([0-9]+)\):")


@dataclass(frozen=True)
class Commit:
    commit: str  # hash
    date: str  # datetime
    author: Author


def git_shortlog(repo: str | Path, kind=None):
    groups = ["--group=author"]  # , "--group=trailer:co-authored-by"
    with sh.pushd(repo):
        summary = sh.git.shortlog(
            *groups,
            full_history=True,
            simplify_merges=True,
            format="%h,%aI",
            _tty_in=True,
            _tty_out=False,
        )
        return shtrip(summary)


def parse_shortlog(summary: str, **csvargs) -> dict[tuple[str, int], list[list[str]]]:
    parts = BLANK_LINE.split(summary.strip())
    commit_summary = {}
    for part in parts:
        match = PART_HEADER.match(part)
        if match is None:
            print(f"couldn't parse part, skipping:\n{part}")
            continue
        author, count = match.groups()
        commits = dedent(part[match.end() :])
        commit_summary[(author, int(count))] = list(
            csv.reader(StringIO(commits.strip()), **csvargs)
        )
    return commit_summary


def shortlog_tbl(commit_summary):
    idcs, cols = zip(*commit_summary.items())
