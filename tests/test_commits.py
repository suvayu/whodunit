from whodunit.commits import git_shortlog, parse_shortlog

from conftest import MM_UNIQ


def test_shortlog(tmp_repo):
    summary = git_shortlog(tmp_repo)
    assert summary
    cs = parse_shortlog(summary, delimiter=",")
    assert len(cs.keys()) == MM_UNIQ
