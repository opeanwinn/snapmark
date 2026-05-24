from dataclasses import dataclass, field
from typing import List
from snapmark.models import BookmarkFolder, Bookmark


@dataclass
class FavoriteResult:
    favorited: List[Bookmark] = field(default_factory=list)
    unfavorited: List[Bookmark] = field(default_factory=list)

    @property
    def favorite_count(self) -> int:
        return len(self.favorited)

    @property
    def unfavorite_count(self) -> int:
        return len(self.unfavorited)

    def summary(self) -> str:
        return (
            f"Favorited: {self.favorite_count} bookmark(s), "
            f"Unfavorited: {self.unfavorite_count} bookmark(s)"
        )


FAVORITE_TAG = "favorite"


def _process_folder(
    folder: BookmarkFolder,
    urls: List[str],
    remove: bool,
    result: FavoriteResult,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            tags = list(child.tags or [])
            if child.url in urls:
                if remove:
                    if FAVORITE_TAG in tags:
                        tags.remove(FAVORITE_TAG)
                        result.unfavorited.append(child)
                else:
                    if FAVORITE_TAG not in tags:
                        tags.append(FAVORITE_TAG)
                        result.favorited.append(child)
            new_children.append(
                Bookmark(
                    title=child.title,
                    url=child.url,
                    tags=tags,
                    added=child.added,
                    notes=child.notes,
                )
            )
        elif isinstance(child, BookmarkFolder):
            new_children.append(
                _process_folder(child, urls, remove, result)
            )
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def favorite_bookmarks(
    root: BookmarkFolder,
    urls: List[str],
) -> tuple[BookmarkFolder, FavoriteResult]:
    result = FavoriteResult()
    new_root = _process_folder(root, urls, remove=False, result=result)
    return new_root, result


def unfavorite_bookmarks(
    root: BookmarkFolder,
    urls: List[str],
) -> tuple[BookmarkFolder, FavoriteResult]:
    result = FavoriteResult()
    new_root = _process_folder(root, urls, remove=True, result=result)
    return new_root, result
