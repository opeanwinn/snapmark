from dataclasses import dataclass, field
from typing import Dict, List, Optional
from snapmark.models import Bookmark, BookmarkFolder


@dataclass
class CategoryResult:
    categorized_count: int = 0
    skipped_count: int = 0
    categories_assigned: Dict[str, int] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Categorized: {self.categorized_count}",
            f"Skipped (already had category): {self.skipped_count}",
        ]
        if self.categories_assigned:
            lines.append("Categories assigned:")
            for cat, count in sorted(self.categories_assigned.items()):
                lines.append(f"  {cat}: {count}")
        return "\n".join(lines)


CATEGORY_RULES: Dict[str, List[str]] = {
    "social": ["twitter.com", "facebook.com", "instagram.com", "linkedin.com", "reddit.com"],
    "development": ["github.com", "gitlab.com", "stackoverflow.com", "dev.to", "pypi.org"],
    "news": ["bbc.com", "cnn.com", "nytimes.com", "theguardian.com", "ycombinator.com"],
    "video": ["youtube.com", "vimeo.com", "twitch.tv", "dailymotion.com"],
    "shopping": ["amazon.com", "ebay.com", "etsy.com"],
}


def _infer_category(url: str) -> Optional[str]:
    url_lower = url.lower()
    for category, domains in CATEGORY_RULES.items():
        for domain in domains:
            if domain in url_lower:
                return category
    return None


def _categorize_folder(
    folder: BookmarkFolder,
    result: CategoryResult,
    overwrite: bool,
) -> BookmarkFolder:
    new_children = []
    for child in folder.children:
        if isinstance(child, Bookmark):
            existing = child.metadata.get("category", "") if child.metadata else ""
            if existing and not overwrite:
                result.skipped_count += 1
                new_children.append(child)
            else:
                category = _infer_category(child.url)
                if category:
                    meta = dict(child.metadata) if child.metadata else {}
                    meta["category"] = category
                    new_children.append(Bookmark(
                        title=child.title,
                        url=child.url,
                        tags=list(child.tags),
                        metadata=meta,
                    ))
                    result.categorized_count += 1
                    result.categories_assigned[category] = (
                        result.categories_assigned.get(category, 0) + 1
                    )
                else:
                    result.skipped_count += 1
                    new_children.append(child)
        elif isinstance(child, BookmarkFolder):
            new_children.append(_categorize_folder(child, result, overwrite))
        else:
            new_children.append(child)
    return BookmarkFolder(name=folder.name, children=new_children)


def categorize_tree(
    root: BookmarkFolder,
    overwrite: bool = False,
) -> tuple[BookmarkFolder, CategoryResult]:
    result = CategoryResult()
    new_root = _categorize_folder(root, result, overwrite)
    return new_root, result
