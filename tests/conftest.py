from pathlib import Path
import shutil

import pytest
import sh

from whodunit.metautils import gen_mailmap, uniq_authors, write_mailmap

TEST_REPO = "https://github.com/calliope-project/calliope.git"

MM_INDICES = [
    (0,),
    (1,),
    (8, 2, 3, 4, 5, 6, 7),
    (9, 10),
    (12, 11),
    (13,),
    (14,),
    (15,),
    (16, 17),
    (18,),
    (19,),
]
MM_COUNT = sum(map(len, MM_INDICES))
MM_UNIQ = len(MM_INDICES)


@pytest.fixture(scope="session")
def tmp_repo(tmp_path_factory):
    path = tmp_path_factory.getbasetemp()
    with sh.pushd(path):
        sh.git.clone(TEST_REPO, "repo")
        repo = path / "repo"
        write_mailmap(gen_mailmap(uniq_authors(repo), MM_INDICES), repo)
        yield repo
        shutil.rmtree(repo)
