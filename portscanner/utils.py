import os


def export_to_file(path: str, content: str) -> None:
    """Write text content to a file, creating parent directories if needed."""
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def copy_to_clipboard(root, content: str) -> None:
    """Replace the current clipboard contents with the given text."""
    root.clipboard_clear()
    root.clipboard_append(content)
