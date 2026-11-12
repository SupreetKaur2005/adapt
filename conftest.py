def pytest_ignore_collect(collection_path, config):
    """Prevent pytest from collecting the non‑python file ``test_output.txt``.
    ``collection_path`` is a :class:`pathlib.Path`; we compare its name.
    """
    return collection_path.name == "test_output.txt"
    """Prevent pytest from trying to collect the non‑python file ``test_output.txt``.
    ``path`` is a :class:`pathlib.Path` instance; ``path.name`` gives the filename.
    """
    return path.name == "test_output.txt"
    """Ignore non‑python test data files that match pytest's collection pattern.
    The project includes a file named ``test_output.txt`` which is mistakenly
    collected as a test module, causing a ``UnicodeDecodeError`` during collection.
    Returning ``True`` for that path tells pytest to skip it.
    """
    return path.basename == "test_output.txt"
