from dataclasses import dataclass, field
from typing import List, Optional
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class ScoreResult:
    scored: List[Bookmark] = field(default_factory=list)
    skipped: int = 0

    @property
    def scored_count(self) -> int:
        return len(self.scored)

    def summary(self) -> str:
        return (
            f"Scored {self.scored_count} bookmark(s), "
            f"skipped {self.skipped} (already scored)."
        )


def _compute_score(bookmark: Bookmark) -> int:
    """Compute a simple quality score (0-100) based on bookmark metadata."""
    score = 0
    if bookmark.url and bookmark.url.startswith("https://"):
        score += 30
    if bookmark.title and len(bookmark.title.strip()) > 3:
        score += 20
    tags = bookmark.metadata.get("tags", [])
    if isinstance(tags, list):
        score += min(len(tags) * 10, 30)
    if bookmark.metadata.get("note"):
        score += 10
    if bookmark.metadata.get("alias"):
        score += 10
    return min(score, 100)


def _score_folder(
    folder: BookmarkFolder,
    result: ScoreResult,
    url_pattern: Optional[str],
    overwrite: bool,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            if url_pattern and url_pattern not in child.url:
                new_children.append(child)
                continue
            if not overwrite and "score" in child.metadata:
                result.skipped += 1
                new_children.append(child)
                continue
            score = _compute_score(child)
            new_meta = {**child.metadata, "score": score}
            updated = Bookmark(
                title=child.title,
                url=child.url,
                metadata=new_meta,
            )
            result.scored.append(updated)
            new_children.append(updated)
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _score_folder(child, result, url_pattern, overwrite)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def score_bookmarks(
    tree: BookmarkFolder,
    url_pattern: Optional[str] = None,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, ScoreResult]:
    result = ScoreResult()
    new_tree = _score_folder(tree, result, url_pattern, overwrite)
    return new_tree, result
