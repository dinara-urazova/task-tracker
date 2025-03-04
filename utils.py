import re


def minify(html: str) -> str:
    """
    Remove line breaks and spaces betweeen HTML tags
    TODO: fix test_minify_line_break and delete pytest.mark.skip
    Example: "<tag> </tag>   " -> "<tag></tag>"
    """
    return re.sub(r">\s+<", "><", html).strip()


class StorageMock:
    def __init__(self, dictionary: dict) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)
