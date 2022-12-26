from itertools import chain
from operator import eq, gt

from whodunit.metautils import gen_mailmap, mailmap_authors, uniq_authors

from conftest import MM_INDICES, MM_COUNT, MM_UNIQ


def test_uniq_authors(tmp_repo):
    assert len(uniq_authors(tmp_repo)) == MM_COUNT


def test_mailmap(tmp_repo):
    mm = gen_mailmap(uniq_authors(tmp_repo), MM_INDICES)
    assert len(mm) == MM_COUNT

    ops_exp = [[eq] + [gt] * (len(i) - 1) for i in MM_INDICES]
    for idx, op in enumerate(chain.from_iterable(ops_exp)):
        msg = f"mailmap:{idx}: field count mismatch, {len(mm[idx])} !{op.__name__!r} 2"
        assert op(len(mm[idx]), 2), msg


def test_mailmap_authors(tmp_repo):
    mm = gen_mailmap(uniq_authors(tmp_repo), MM_INDICES)
    authors = mailmap_authors(mm)
    assert len(authors) == MM_UNIQ
