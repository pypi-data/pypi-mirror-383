from __future__ import annotations

import re
from typing import Any

import astdoc.markdown
from markdown import Extension, Markdown
from markdown.preprocessors import Preprocessor

# Regex to match CJK characters
# (Hiragana, Katakana, CJK Unified Ideographs, and some punctuation)
# This pattern covers a good range of CJK characters.
# \u3000-\u303f: CJK Symbols and Punctuation
# \u3040-\u309f: Hiragana
# \u30a0-\u30ff: Katakana
# \u4e00-\u9fff: CJK Unified Ideographs
CJK_CHAR_PATTERN = r"[\u3000-\u30ff\u4e00-\u9fff]"

# CJK_CHAR + newline + space* + CJK_CHAR
REPLACE_PATTERN = re.compile(f"({CJK_CHAR_PATTERN})\\n *({CJK_CHAR_PATTERN})")


def replace(match: re.Match[str]) -> str:
    return f"{match.group(1)}{match.group(2)}"


class CjkAutojoinPreprocessor(Preprocessor):
    def run(self, lines: list[str]) -> list[str]:
        text = "\n".join(lines)
        text = astdoc.markdown.sub(REPLACE_PATTERN, replace, text)
        return text.split("\n")


class CjkAutojoinExtension(Extension):
    def extendMarkdown(self, md: Markdown) -> None:
        """Add CjkAutojoinPreprocessor to the Markdown instance."""
        # Priority 27: Runs after NormalizeWhitespace (priority 30) and
        # before HtmlBlockPreprocessor (priority 20).
        md.preprocessors.register(CjkAutojoinPreprocessor(md), "cjk_autojoin", 27)


def makeExtension(**kwargs: Any) -> CjkAutojoinExtension:
    return CjkAutojoinExtension(**kwargs)
