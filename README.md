# snapmark

A Python utility to snapshot and restore browser bookmark trees via JSON exports.

---

## Installation

```bash
pip install snapmark
```

## Usage

Snapshot your current browser bookmarks to a JSON file:

```bash
snapmark snapshot --browser chrome --output bookmarks.json
```

Restore bookmarks from a previously saved snapshot:

```bash
snapmark restore --input bookmarks.json --browser chrome
```

You can also list available snapshots:

```bash
snapmark list
```

### Example

```python
from snapmark import BookmarkSnapshot

snapshot = BookmarkSnapshot(browser="chrome")
snapshot.save("my_bookmarks.json")

# Later, restore from the snapshot
snapshot.load("my_bookmarks.json")
snapshot.restore()
```

## Supported Browsers

- Google Chrome
- Mozilla Firefox
- Microsoft Edge

## Requirements

- Python 3.8+
- A supported browser installed locally

## License

This project is licensed under the [MIT License](LICENSE).

---

> **Note:** Always back up your existing bookmarks before performing a restore operation.