import pytest

from whodunit.diffs import git_diffstat, parse_re_groups, TRIM_NOPRINT


@pytest.mark.parametrize(
    "line, expect",
    [
        (
            "0\t0\ttest/{foo.yaml => bar.yaml}",
            ("test/foo.yaml", 0, 0, "test/bar.yaml"),
        ),
        (
            "5\t2\trequirements/base.yml => requirements.yml",
            ("requirements/base.yml", 5, -2, "requirements.yml"),
        ),
        (
            "10\t2\ttop/{foo/bar.py => bar/baz.py}",
            ("top/foo/bar.py", 10, -2, "top/bar/baz.py"),
        ),
        (
            "0\t0\ttop/{foo => bar}/module.py",
            ("top/foo/module.py", 0, 0, "top/bar/module.py"),
        ),
        (
            "3\t3\ttop/{foo => }/package/__init__.py",
            ("top/foo/package/__init__.py", 3, -3, "top/package/__init__.py"),
        ),
        (
            "3\t3\ttop/{ => foo}/package/__init__.py",
            ("top/package/__init__.py", 3, -3, "top/foo/package/__init__.py"),
        ),
    ],
    ids=range(6),
)
def test_parse_re_groups(line, expect):
    match = TRIM_NOPRINT.match(line)
    if match:
        assert parse_re_groups(match) == expect


@pytest.mark.parametrize(
    "commit, expected",
    [
        ("23c7039", (11, (5,))),
        ("71dc40f", (10, (6, 9))),
        ("f55a823", (36, (*range(12, 25), *range(32, 35)))),
    ],
)
def test_diffstat(tmp_repo, commit, expected):
    stat = git_diffstat(tmp_repo, commit)
    assert len(stat.files) == expected[0]
    for i in expected[1]:
        assert stat.renamed[i], f"missed rename: {stat.renamed[i]}"
