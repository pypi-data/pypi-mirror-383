import os
import re
import time
from dataclasses import dataclass
from enum import auto, StrEnum
from typing import Callable, Iterable, TypeVar

import git


@dataclass
class Version:
    major: int
    minor: int
    patch: int
    unreleased_commit_count: int = 0
    head_rev: str = ''
    dirty_marker: str = ''

    def __str__(self) -> str:
        text = f'{self.major}.{self.minor}.{self.patch}'

        if self.unreleased_commit_count > 0 or self.dirty_marker:
            text += f'.dev{self.unreleased_commit_count}+g{self.head_rev}'

        if self.dirty_marker:
            text += f'.d{self.dirty_marker}'

        return text

    @staticmethod
    def parse(version_str: str) -> 'Version':
        match = re.match(r'(\d+)\.(\d+)\.(\d+)(?:\.dev(\d+)\+g([0-9a-f]+))?(?:\.d(\d+))?', version_str)
        if not match:
            raise ValueError(f'Invalid version string: {version_str}')

        major, minor, patch, unreleased_commit_count, head_rev, dirty_marker = match.groups()
        return Version(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            unreleased_commit_count=int(unreleased_commit_count) if unreleased_commit_count else 0,
            head_rev=head_rev if head_rev else '',
            dirty_marker=dirty_marker if dirty_marker else ''
        )

RELEASE_BRANCH = 'main'
BASE_VERSION = Version(major=1, minor=0, patch=1)
BASE_COMMIT = 'fc5763e933e97ca1d014bd1afe2ad6e744645158'


class VersionIncrementType(StrEnum):
    NoIncrement = auto()
    Patch = auto()
    Minor = auto()
    Major = auto()


VersionIncrementMap = [
    (r'^\w+(\([\w\s]*\))!:.*$', VersionIncrementType.Major),
    (r'^feat(\([\w\s]*\))?:.*$', VersionIncrementType.Minor),
    (r'^fix(\([\w\s]*\))?:.*$', VersionIncrementType.Patch),
]


def get_commit_increment(commit: git.Commit) -> VersionIncrementType:
    for pattern, increment in VersionIncrementMap:
        if re.search(pattern, commit.message.splitlines()[0]):
            return increment
    return VersionIncrementType.NoIncrement


T = TypeVar('T')


def takewhile_inclusive(predicate: Callable[[T], bool], iterable: Iterable[T]):
    for x in iterable:
        yield x
        if not predicate(x):
            break

        
def get_repo_version(repo: git.Repo) -> Version:
    if not repo.tags:
        repo.remotes.origin.fetch(tags=True)

    version_tags = {tag.commit.hexsha: tag for tag in repo.tags if re.match(r'v\d+\.\d+\.\d+', tag.name)}

    commits = list(reversed(list(takewhile_inclusive(lambda x: x.hexsha not in version_tags, repo.iter_commits()))))
    version = Version.parse(version_tags[commits[0].hexsha].name[1:])

    for commit in commits[1:]:
        match get_commit_increment(commit):
            case VersionIncrementType.Major:
                version = Version(major=version.major + 1, minor=0, patch=0)
            case VersionIncrementType.Minor:
                version = Version(major=version.major, minor=version.minor + 1, patch=0)
            case VersionIncrementType.Patch:
                version = Version(major=version.major, minor=version.minor, patch=version.patch + 1)
            case _:
                pass

    dirty_marker = ''
    head_rev = repo.git.rev_parse(repo.head.commit.hexsha, short=4)
    unreleased_commit_count = 0

    if not repo.head.is_detached and repo.active_branch.name != RELEASE_BRANCH:
        merge_base = repo.git.merge_base(f'origin/{RELEASE_BRANCH}', 'HEAD')
        rev_list = repo.git.rev_list(f'{repo.head.name}...{merge_base}', count=True)
        unreleased_commit_count = int(rev_list)
    if repo.is_dirty() and unreleased_commit_count == 0:
        unreleased_commit_count = 1

    if repo.is_dirty():
        dirty_marker = time.strftime(
            "%Y%m%d",
            time.gmtime(int(os.environ.get('SOURCE_DATE_EPOCH', time.time())))
        )

    return Version(major=version.major, minor=version.minor, patch=version.patch, unreleased_commit_count=unreleased_commit_count, head_rev=head_rev, dirty_marker=dirty_marker)


try:
    __version__ = str(get_repo_version(git.Repo('.')))
except Exception as e:
    __version__ = '0.0.1-unknown'
    