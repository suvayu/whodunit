from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

import sh


def shtrip(output: sh.RunningCommand | None) -> str:
    """Strip shell stdout of newlines & whitespace"""
    if output is None:
        return ""
    return repr(output).strip()


@dataclass(frozen=True)
class Author:
    name: str
    email: str

    def __iter__(self):
        return iter((self.name, self.email))


def uniq_authors(repo: str | Path) -> list[Author]:
    with sh.pushd(repo):
        records = sh.sort(
            sh.git.log(format="%an <%ae>", _tty_out=False, _piped=True), "-u"
        )
    return list(Author(*i.strip("'").rsplit(maxsplit=1)) for i in records.splitlines())


def print_authors(records: list[Author]):
    list(map(print, (f"{i:2d} - {a}" for i, a in enumerate(records))))


def gen_mailmap(
    records: list[Author], committer_sets: list[tuple[int]]
) -> list[tuple[str, ...]]:
    lines: list[tuple[str, ...]] = []
    for indices in committer_sets:
        rows: list[tuple[str, ...]] = []
        for i, j in enumerate(indices):
            if i == 0:
                rows += [tuple(records[j])]
            elif rows[0][0] == records[j].name:  # name matches
                rows += [(*rows[0], records[j].email)]
            else:
                rows += [(*rows[0], *records[j])]
        lines += rows
    return lines


def write_mailmap(records: list[tuple[str, ...]], repo: str | Path):
    mailmap = Path(repo) / ".mailmap"
    mailmap.write_text("\n".join(" ".join(row) for row in records) + "\n")


def mailmap_authors(records: list[tuple[str, ...]]) -> set[Author]:
    return {Author(name, email) for name, email, *_ in records}
