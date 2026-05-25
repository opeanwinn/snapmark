"""Compare two named snapshots and report bookmark-level differences."""

from dataclasses import dataclass, field
from typing import List, Tuple

from snapmark.snapshot import load_snapshot
from snapmark.diff import diff_trees, DiffResult
from snapmark.models import BookmarkFolder


@dataclass
class SnapshotDiffResult:
    snapshot_a: str
    snapshot_b: str
    diff: DiffResult

    def summary(self) -> str:
        lines = [
            f"Comparing '{self.snapshot_a}' → '{self.snapshot_b}'",
            f"  Added   : {len(self.diff.added)}",
            f"  Removed : {len(self.diff.removed)}",
            f"  Modified: {len(self.diff.modified)}",
        ]
        return "\n".join(lines)

    def has_changes(self) -> bool:
        return self.diff.has_changes()


def compare_snapshots(
    name_a: str,
    name_b: str,
    snapshot_dir: str = ".snapmarks",
) -> SnapshotDiffResult:
    """Load two snapshots by name and diff their bookmark trees."""
    tree_a: BookmarkFolder = load_snapshot(name_a, snapshot_dir=snapshot_dir)
    tree_b: BookmarkFolder = load_snapshot(name_b, snapshot_dir=snapshot_dir)
    diff = diff_trees(tree_a, tree_b)
    return SnapshotDiffResult(snapshot_a=name_a, snapshot_b=name_b, diff=diff)
