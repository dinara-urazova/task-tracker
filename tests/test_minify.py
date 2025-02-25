import pytest
from utils import minify


def test_minify() -> None:
    html = """
    <h1>Hello world</h1>
    <p>Lorem ipsum</p>
"""
    assert minify(html) == "<h1>Hello world</h1><p>Lorem ipsum</p>"


@pytest.mark.skip(reason="need to implement a line break between tag attributes")
def test_minify_line_break() -> None:
    html = """
    <textarea id="task_description" name="task_description" rows="10" cols="30" required minlength="3" maxlength="2000"></textarea><br><br>
"""
    assert (
        minify(html)
        == '<textarea id="task_description" name="task_description" rows="10" cols="30" required minlength="3" maxlength="2000"></textarea><br><br>'
    )
