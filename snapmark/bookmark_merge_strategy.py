from dataclasses import dataclass, field
from typing import List, Literal
from snapmark.models import BookmarkFolder, Bookmark

MergeStrategy = Literal["keep_base", "keep_incoming", "keep_both"]


@dataclass
class StrategyMergeResult:
    root: BookmarkFolder
    merged_count: int = 0
    skipped_count: int = 0
    conflicts: List[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"Merged:   {self.merged_count}",
            f"Skipped:  {self.skipped_count}",
            f"Conflicts: {len(self.conflicts)}",
        ]
        if self.conflicts:
            lines.append("Conflict URLs:")
            for url in self.conflicts:
                lines.append(f"  - {url}")
        return "\n".join(lines)


def _merge_folder(
    base: BookmarkFolder,
    incoming: BookmarkFolder,
    strategy: MergeStrategy,
    result: StrategyMergeResult,
) -> BookmarkFolder:
    base_urls = {b.url: b for b in base.children if isinstance(b, Bookmark)}
    incoming_urls = {b.url: b for b in incoming.children if isinstance(b, Bookmark)}

    merged_bookmarks: list = []
    seen_urls: set = set()

    for url, bm in base_urls.items():
        if url in incoming_urls:
            conflict_bm = incoming_urls[url]
            if bm.title != conflict_bm.title or bm.tags != conflict_bm.tags:
                result.conflicts.append(url)
                if strategy == "keep_base":
                    merged_bookmarks.append(bm)
                    result.skipped_count += 1
                elif strategy == "keep_incoming":
                    merged_bookmarks.append(conflict_bm)
                    result.merged_count += 1
                elif strategy == "keep_both":
                    merged_bookmarks.append(bm)
                    merged_bookmarks.append(
                        Bookmark(
                            title=f"{conflict_bm.title} (incoming)",
                            url=conflict_bm.url + "#incoming",
                            tags=conflict_bm.tags,
                            metadata=conflict_bm.metadata,
                        )
                    )
                    result.merged_count += 1
            else:
                merged_bookmarks.append(bm)
                result.merged_count += 1
        else:
            merged_bookmarks.append(bm)
            result.merged_count += 1
        seen_urls.add(url)

    for url, bm in incoming_urls.items():
        if url not in seen_urls:
            merged_bookmarks.append(bm)
            result.merged_count += 1

    base_folders = {f.name: f for f in base.children if isinstance(f, BookmarkFolder)}
    incoming_folders = {f.name: f for f in incoming.children if isinstance(f, BookmarkFolder)}

    merged_folders: list = []
    for name, bf in base_folders.items():
        if name in incoming_folders:
            merged_folders.append(_merge_folder(bf, incoming_folders[name], strategy, result))
        else:
            merged_folders.append(bf)

    for name, inf in incoming_folders.items():
        if name not in base_folders:
            merged_folders.append(inf)

    return BookmarkFolder(name=base.name, children=merged_bookmarks + merged_folders)


def merge_with_strategy(
    base: BookmarkFolder,
    incoming: BookmarkFolder,
    strategy: MergeStrategy = "keep_base",
) -> StrategyMergeResult:
    result = StrategyMergeResult(root=base)
    merged_root = _merge_folder(base, incoming, strategy, result)
    result.root = merged_root
    return result
