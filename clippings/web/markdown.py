from markdown_it import MarkdownIt

md_safe_renderer = MarkdownIt("zero").enable(["list", "emphasis", "backticks", "fence"])


def render_safe(markdown: str) -> str:
    return md_safe_renderer.render(markdown)
