"""Data models for bookmark tree structures."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import uuid


@dataclass
class Bookmark:
    """Represents a single bookmark entry."""

    title: str
    url: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    add_date: Optional[int] = None
    icon: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": "bookmark",
            "title": self.title,
            "url": self.url,
            "add_date": self.add_date,
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Bookmark":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data["title"],
            url=data["url"],
            add_date=data.get("add_date"),
            icon=data.get("icon"),
        )


@dataclass
class BookmarkFolder:
    """Represents a folder that can contain bookmarks or sub-folders."""

    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    children: List["BookmarkFolder | Bookmark"] = field(default_factory=list)
    add_date: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": "folder",
            "title": self.title,
            "add_date": self.add_date,
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BookmarkFolder":
        folder = cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data["title"],
            add_date=data.get("add_date"),
        )
        for child in data.get("children", []):
            if child.get("type") == "folder":
                folder.children.append(BookmarkFolder.from_dict(child))
            else:
                folder.children.append(Bookmark.from_dict(child))
        return folder
