import pytest

from clippings.web.markdown import render_safe


@pytest.mark.parametrize(
    "input_text,must_contain",
    [
        ("abc", "<p>"),
        ("**bold**", "<strong>"),
        ("*italic*", "<em>"),
        ("- item", "<ul>"),
        ("1. item", "<ol>"),
        ("`code`", "<code>"),
        ("```\ncode\n```", "<pre><code>"),
    ],
)
def test_render_allowed_tags(input_text, must_contain):
    result = render_safe(input_text)

    assert must_contain in result


def test_dont_render_html_tags():
    result = render_safe("<script>alert('XSS')</script>")

    assert "<script>" not in result


@pytest.mark.parametrize(
    "input_text",
    [
        "# heading 1",
        "## heading 2",
        "### heading 3",
        "#### heading 4",
        "##### heading 5",
        "###### heading 6",
    ],
)
def test_dont_render_unallowed_tags(input_text):
    result = render_safe(input_text)

    assert input_text in result
