from dataclasses import dataclass
import re
from pathlib import Path
from typing import Match

import sh

from whodunit.metautils import shtrip


TRIM_NOPRINT = re.compile(
    r"(?:^.+[^\x20-\xff])*([0-9]+)\s+([0-9]+)\s+([\x20-\xff]+)(?:[^\x20-\xff].+$)*"
)
RENAME_REGEX = re.compile(r"(.+/)?\{(.+)? => (.+)?\}(.+)?|(.+)? => (.+)?")


def parse_re_groups(diff_match: Match[str]) -> tuple[str, int, int, str]:
    add, sub, _file = diff_match.groups()
    renamed = ""
    if path_match := RENAME_REGEX.match(_file):
        src, dst = [], []
        parts = path_match.groups()
        part1 = parts[:4]
        part2 = parts[4:]
        if any(part1):
            for i, part in enumerate(parts):
                if part is None:
                    continue
                part = part.rstrip("/")
                if i != 2:
                    src.append(part)
                if i != 1:
                    dst.append(part)
            _file = "/".join(src).replace("//", "/")
            renamed = "/".join(dst).replace("//", "/")
        if any(part2):
            _file, renamed = part2
    return _file, int(add), -int(sub), renamed


@dataclass
class DiffStat:
    commit: str
    files: tuple[str, ...]
    additions: tuple[int, ...]
    deletions: tuple[int, ...]
    renamed: tuple[str, ...]


def git_diffstat(repo: str | Path, commit: str) -> DiffStat:
    if ".." in commit:
        cmd = ["-c", "pager.diff=false", "diff", commit]
    else:
        cmd = ["-c", "pager.show=false", "show", commit]
    with sh.pushd(repo):
        output = shtrip(
            sh.git(*cmd, no_color=True, numstat=True, format="", _tty_out=False)
        )
        files: tuple[str, ...]
        additions: tuple[int, ...]
        deletions: tuple[int, ...]
        renamed: tuple[str, ...]
        files, additions, deletions, renamed = zip(
            *map(
                parse_re_groups,
                filter(
                    None, (TRIM_NOPRINT.match(line) for line in output.splitlines())
                ),
            )
        )
    return DiffStat(commit, files, additions, deletions, renamed)
